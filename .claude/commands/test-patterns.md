# Test Regex Patterns

Test the regex patterns for a specific log type by analyzing sample data and validating pattern matches.

## Usage
```
/test-patterns [log_type]
```

## Examples
- `/test-patterns OFFICE_365` - Test Office 365 timestamp patterns
- `/test-patterns AWS_CLOUDTRAIL` - Test AWS CloudTrail patterns

## What it does
1. Loads the specified log type's patterns from `logtypes_events_timestamps.yaml`
2. Reads the corresponding log file (e.g., `OFFICE_365.log`)
3. Tests each regex pattern against the log data
4. Reports matches, capture groups, and any pattern issues
5. Suggests improvements if patterns don't match expected data

This helps validate that regex patterns work correctly with sample log data and identifies any issues with pattern definitions.