#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import re
import yaml
import os
from collections import defaultdict
import hashlib
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, cors_allowed_origins="*")

# Create uploads directory if it doesn't exist
os.makedirs('uploads', exist_ok=True)

# Cache for processed log files
log_cache = {}
# Store uploaded file content in memory
uploaded_files = {}

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
    log_types = list(config.keys())
    return render_template('index.html', log_types=log_types)

@app.route('/api/log-content/<log_type>')
def get_log_content(log_type):
    """Get log file content"""
    lines = read_log_file(log_type)
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
def upload_log():
    """Handle log file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    log_type = request.form.get('log_type')
    if not log_type:
        return jsonify({'error': 'No log type specified'}), 400
    
    try:
        # Read file content into memory
        content = file.read().decode('utf-8', errors='ignore')
        lines = content.splitlines(keepends=True)
        
        # Store in memory
        uploaded_files[log_type] = lines
        
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
    
    lines = read_log_file(log_type)
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

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)