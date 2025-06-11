# Debug Regex Patterns

Debug regex patterns that aren't working correctly by testing them against sample data and suggesting fixes.

## Usage
```
/debug-patterns [log_type] [pattern_name]
```

## Examples
- `/debug-patterns OFFICE_365 creation_time` - Debug the CreationTime pattern
- `/debug-patterns AWS_CLOUDTRAIL event_time` - Debug AWS event time pattern

## What it does
1. Loads the specific pattern from the YAML configuration
2. Tests the pattern against sample log data
3. Shows what the regex is matching (or not matching)
4. Analyzes capture groups and their positions
5. Suggests improvements to fix pattern issues
6. Tests suggested fixes to verify they work
7. Provides updated YAML configuration if needed

This helps troubleshoot regex patterns that aren't extracting timestamps correctly or are failing to match expected log formats.