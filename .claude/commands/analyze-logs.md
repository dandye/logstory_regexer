# Analyze Log File

Analyze a log file to identify potential timestamp patterns and suggest regex patterns for extraction.

## Usage
```
/analyze-logs [file_path]
```

## Examples
- `/analyze-logs ./custom_app.log` - Analyze a custom application log
- `/analyze-logs ./uploads/new_format.log` - Analyze an uploaded log file

## What it does
1. Reads the specified log file
2. Identifies potential timestamp formats using common patterns
3. Suggests regex patterns for timestamp extraction
4. Shows sample matches and capture groups
5. Recommends which patterns would work best for the LogStory visualizer
6. Optionally generates a new log type configuration

This is useful for understanding new log formats and determining how to configure the regex visualizer to work with them.