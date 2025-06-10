# LogStory Regex Visualizer

A web application for visualizing regex pattern matches in log files with real-time editing and color-coded highlighting.

## Features

- Load regex patterns from YAML configuration
- Real-time pattern editing with validation
- Color-coded visualization of regex matches
- Separate colors for capture groups
- WebSocket support for responsive updates
- Support for multiple log types

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Select a log type (e.g., OFFICE_365)

4. Click "Load Patterns" to load regex patterns from the YAML configuration

5. Edit patterns or add new ones

6. Click "Analyze" to visualize matches in the log file

## How it works

- Each regex pattern is assigned a unique color based on its name
- Full pattern matches are highlighted with a semi-transparent background
- Capture groups within each match are highlighted with modified colors
- Hover over highlighted text to see if it's a full match or capture group
- The legend shows all active patterns with their colors

## Configuration

Regex patterns are stored in `logtypes_events_timestamps.yaml`. Each log type contains a list of timestamp patterns with:
- `name`: Pattern identifier
- `pattern`: Regular expression pattern
- `group`: Which capture group contains the timestamp
- `dateformat` or `epoch`: Time format information