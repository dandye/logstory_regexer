# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Application Architecture

This is a Flask-based LogStory Regex Visualizer that provides real-time visualization of regex pattern matches in log files. The application uses Flask-SocketIO for bidirectional real-time communication between frontend and backend.

### Core Components

**Backend (app.py):**
- Flask web server with RESTful API endpoints
- Flask-SocketIO for real-time pattern analysis via WebSocket
- YAML-driven configuration system for 30+ log types
- Dual file source support: static files and uploaded files
- Caching system based on file modification time and size
- Regex processing engine with capture group extraction

**Frontend:**
- Single-page application with dynamic pattern management
- Real-time highlighting of regex matches with color coding
- File upload interface with progress feedback
- Responsive design using CSS Grid

**Configuration:**
- `logtypes_events_timestamps.yaml` defines log types and timestamp patterns
- Each log type contains patterns with metadata (name, regex, capture groups, date formats)
- Configuration is loaded dynamically, no code changes needed for new log types

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Development server with debug mode
python app.py

# Production server (if needed)
gunicorn --worker-class eventlet -w 1 app:app
```

### Testing
```bash
# Install updated dependencies
pip install -r requirements.txt --upgrade

# Test file upload functionality
curl -X POST -F "file=@test.log" -F "log_type=OFFICE_365" http://localhost:5000/api/upload-log

# Validate YAML configuration
python -c "import yaml; yaml.safe_load(open('logtypes_events_timestamps.yaml', 'r'))"
```

## Key Architecture Patterns

### Real-time Communication Flow
1. Client connects via SocketIO and selects log type
2. Client emits `analyze_patterns` event with patterns and line limit
3. Server processes file (cached or uploaded) and applies regex patterns
4. Server emits `analysis_results` with match data including positions and capture groups
5. Frontend renders highlighted matches with color-coded capture groups

### File Processing Architecture
- Files can be uploaded (stored in memory) or read from filesystem
- Caching uses `{filename}_{mtime}_{size}` as cache key
- File processing limits configurable via `line_limit` parameter (default 100, supports up to 10,000)
- UTF-8 decoding with error handling for corrupted log entries

### Pattern Management System
- Patterns are applied in sequence to each log line
- Each pattern generates matches with start/end positions
- Capture groups are extracted and assigned colors
- Color generation uses MD5 hash for consistency across sessions

## Configuration Management

### Adding New Log Types
Add to `logtypes_events_timestamps.yaml`:
```yaml
NEW_LOG_TYPE:
  api: unstructuredlogentries
  timestamps:
    - name: "Descriptive Pattern Name"
      base_time: true
      pattern: 'regex_pattern_here'
      group: 1
      dateformat: "%Y-%m-%d %H:%M:%S"
```

### Pattern Structure Requirements
- `name`: Human-readable pattern identifier
- `pattern`: Valid Python regex with capture groups
- `group`: Capture group number for timestamp extraction
- `dateformat`: Python strftime format or `epoch: true` for Unix timestamps
- `base_time`: Boolean indicating primary timestamp pattern

## Security Considerations

- File uploads limited to 50MB (`MAX_CONTENT_LENGTH`)
- Filename sanitization using `secure_filename()`
- CORS enabled for development (`cors_allowed_origins="*"`)
- Error handling prevents regex injection through pattern validation
- UTF-8 decoding with `errors='ignore'` for malformed files

## Performance Notes

- File caching reduces disk I/O for repeated analysis
- Line limit prevents performance issues with large files
- SocketIO events are non-blocking for better user experience
- Static file serving handled by Flask development server (use reverse proxy in production)

## Common Development Tasks

### Extending Regex Processing
Modify `apply_regex_patterns()` function to add new match types or metadata extraction.

### Adding New Highlight Styles
Add CSS classes in `static/css/style.css` and update `applyHighlights()` function in `static/js/app.js`.

### Debugging SocketIO Communication
Use browser developer tools Network tab to monitor WebSocket frames, or add logging to SocketIO event handlers.

### Configuration Validation
Use the YAML validation command above to check syntax before deploying configuration changes.