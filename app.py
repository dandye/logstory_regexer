#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import re
import yaml
import os
from collections import defaultdict
import hashlib
from werkzeug.utils import secure_filename
from datetime import timedelta

# Import authentication and storage modules
from auth import (
    login_required, get_current_user_id, get_current_user,
    login_user, logout_user, verify_google_token
)
from storage import (
    upload_file_to_gcs, get_file_from_gcs, 
    list_user_files, generate_signed_url
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Sessions last 7 days
app.config['SESSION_COOKIE_SECURE'] = True  # Require HTTPS in production
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS attacks
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection
socketio = SocketIO(app, cors_allowed_origins="*")

# Cache for processed log files
log_cache = {}
# Store uploaded file content in memory per user session
uploaded_files = {}  # Now keyed by (user_id, log_type)

def get_color_for_string(s):
    """Generate a consistent color for a string using hash"""
    hash_obj = hashlib.md5(s.encode())
    hash_hex = hash_obj.hexdigest()
    # Use first 6 characters as color
    return f"#{hash_hex[:6]}"

def load_yaml_config():
    """Load the YAML configuration file"""
    with open('logtypes_events_timestamps.yaml', 'r') as f:
        return yaml.safe_load(f)

def read_log_file(log_type):
    """Read log file based on log type"""
    # First check if we have an uploaded file for this log type
    if log_type in uploaded_files:
        return uploaded_files[log_type]
    
    # Otherwise, try to read from file system
    log_file = f"{log_type}.log"
    if not os.path.exists(log_file):
        return []
    
    # Check cache
    file_stat = os.stat(log_file)
    cache_key = f"{log_file}_{file_stat.st_mtime}_{file_stat.st_size}"
    
    if cache_key in log_cache:
        return log_cache[cache_key]
    
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    
    # Cache the result
    log_cache[cache_key] = lines
    return lines

def apply_regex_patterns(text, patterns):
    """Apply regex patterns to text and return matches with colors"""
    results = []
    
    for i, pattern_info in enumerate(patterns):
        pattern = pattern_info.get('pattern', '')
        pattern_name = pattern_info.get('name', f'Pattern {i+1}')
        
        try:
            regex = re.compile(pattern)
            matches = []
            
            for match in regex.finditer(text):
                match_data = {
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(0),
                    'pattern_name': pattern_name,
                    'pattern_index': i,
                    'groups': []
                }
                
                # Get all groups
                for g_idx in range(1, len(match.groups()) + 1):
                    group = match.group(g_idx)
                    if group is not None:
                        match_data['groups'].append({
                            'index': g_idx,
                            'text': group,
                            'start': match.start(g_idx),
                            'end': match.end(g_idx)
                        })
                
                matches.append(match_data)
            
            if matches:
                results.append({
                    'pattern': pattern,
                    'name': pattern_name,
                    'matches': matches,
                    'color': get_color_for_string(pattern_name)
                })
        except re.error as e:
            # Invalid regex pattern
            pass
    
    return results

@app.route('/')
def index():
    """Main page"""
    config = load_yaml_config()
    log_types = sorted(config.keys())
    user = get_current_user()
    return render_template('index.html', log_types=log_types, user=user)

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html', config={'GOOGLE_CLIENT_ID': os.environ.get('GOOGLE_CLIENT_ID')})

@app.route('/auth/google', methods=['POST'])
def google_auth():
    """Handle Google Sign-In authentication"""
    token = request.json.get('credential')
    if not token:
        return jsonify({'error': 'No token provided'}), 400
    
    user_info = verify_google_token(token)
    if not user_info:
        return jsonify({'error': 'Invalid token'}), 401
    
    # Log the user in
    login_user(user_info)
    
    return jsonify({
        'success': True,
        'user': user_info,
        'redirect': url_for('index')
    })

@app.route('/logout')
def logout():
    """Logout current user"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/api/log-content/<log_type>')
@login_required
def get_log_content(log_type):
    """Get log file content"""
    user_id = get_current_user_id()
    lines = read_log_file(log_type, user_id)
    return jsonify({
        'content': ''.join(lines[:1000]),  # Limit to first 1000 lines
        'total_lines': len(lines)
    })

@app.route('/api/patterns/<log_type>')
def get_patterns(log_type):
    """Get regex patterns for a log type"""
    config = load_yaml_config()
    if log_type not in config:
        return jsonify({'error': 'Log type not found'}), 404
    
    timestamps = config[log_type].get('timestamps', [])
    return jsonify({'patterns': timestamps})

@app.route('/api/upload-log', methods=['POST'])
@login_required
def upload_log():
    """Handle log file upload with user-specific storage"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    log_type = request.form.get('log_type')
    if not log_type:
        return jsonify({'error': 'No log type specified'}), 400
    
    user_id = get_current_user_id()
    
    try:
        # Secure the filename
        filename = secure_filename(f"{log_type}.log")
        
        # Upload to GCS
        result = upload_file_to_gcs(
            file_content=file,
            user_id=user_id,
            filename=filename,
            content_type='text/plain'
        )
        
        if not result['success']:
            return jsonify({'error': result.get('error', 'Upload failed')}), 500
        
        # Also read into memory for immediate use
        file.seek(0)  # Reset file pointer after upload
        content = file.read().decode('utf-8', errors='ignore')
        lines = content.splitlines(keepends=True)
        
        # Store in memory with user ID
        user_file_key = (user_id, log_type)
        uploaded_files[user_file_key] = lines
        
        return jsonify({
            'success': True,
            'lines': len(lines),
            'size': len(content)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('analyze_patterns')
def handle_analyze_patterns(data):
    """Analyze patterns in real-time"""
    log_type = data.get('log_type')
    patterns = data.get('patterns', [])
    line_limit = data.get('line_limit', 100)
    
    # Get user ID from session
    user_id = get_current_user_id()
    lines = read_log_file(log_type, user_id)
    results = []
    
    for i, line in enumerate(lines[:line_limit]):
        line_results = apply_regex_patterns(line, patterns)
        # Always include the line, even if no matches
        results.append({
            'line_number': i + 1,
            'line': line.rstrip(),
            'matches': line_results
        })
    
    emit('analysis_results', {
        'results': results,
        'total_lines': len(lines),
        'analyzed_lines': min(line_limit, len(lines))
    })

@app.route('/api/user-files')
@login_required
def get_user_files():
    """Get list of files for current user"""
    user_id = get_current_user_id()
    files = list_user_files(user_id)
    return jsonify({'files': files})

@app.route('/api/file-url/<filename>')
@login_required
def get_file_url(filename):
    """Generate signed URL for file access"""
    user_id = get_current_user_id()
    signed_url = generate_signed_url(user_id, filename, expiration_hours=1)
    
    if signed_url:
        return jsonify({
            'success': True,
            'url': signed_url
        })
    else:
        return jsonify({
            'success': False,
            'error': 'File not found or access denied'
        }), 404

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)