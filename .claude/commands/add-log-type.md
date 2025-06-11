# Add Log Type

Add a new log type configuration with timestamp patterns to support additional log formats.

## Usage
```
/add-log-type [log_type_name]
```

## Examples
- `/add-log-type NGINX` - Add support for Nginx access logs
- `/add-log-type APACHE` - Add support for Apache access logs
- `/add-log-type CUSTOM_APP` - Add support for custom application logs

## What it does
1. Prompts for sample log entries to analyze timestamp patterns
2. Helps identify appropriate regex patterns for timestamp extraction
3. Adds the new log type configuration to `logtypes_events_timestamps.yaml`
4. Creates a sample log file with the provided entries
5. Tests the patterns to ensure they work correctly
6. Updates documentation if needed

This streamlines the process of adding support for new log formats by automating pattern creation and validation.