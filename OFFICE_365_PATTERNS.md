# Office 365 Log Pattern Demo

This document explains the Office 365 timestamp patterns and provides sample logs for testing the regex visualizer.

## Available Patterns

The Office 365 log type supports three timestamp patterns defined in `logtypes_events_timestamps.yaml`:

### 1. CreationTime Pattern (Primary)
- **Name**: `creation_time`
- **Pattern**: `("CreationTime":\s*")(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})`
- **Format**: `%Y-%m-%dT%H:%M:%S`
- **Description**: Primary timestamp indicating when the audit event was created
- **Example Match**: `"CreationTime": "2024-01-15T09:30:45"`

### 2. LabelAppliedDateTime Pattern
- **Name**: `label_applied`
- **Pattern**: `("LabelAppliedDateTime":\s*")(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})`
- **Format**: `%Y-%m-%dT%H:%M:%S`
- **Description**: Timestamp when a sensitivity label was applied to content
- **Example Match**: `"LabelAppliedDateTime": "2024-01-15T09:32:05"`

### 3. Sent Pattern
- **Name**: `sent`
- **Pattern**: `("Sent":\s*")(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})`
- **Format**: `%Y-%m-%dT%H:%M:%S`
- **Description**: Timestamp when an email was sent
- **Example Match**: `"Sent": "2024-01-15T09:34:52"`

## Sample Log Files

### OFFICE_365_demo.log
A demonstration file containing 20 sample Office 365 audit log entries with:
- **CreationTime** fields in every entry (primary pattern)
- **LabelAppliedDateTime** fields in sensitivity label operations
- **Sent** fields in email-related operations

### OFFICE_365.log
The original Office 365 audit log file with real Azure Active Directory events showing role assignments and administrative actions.

## How to Test

1. **Start the application**: `python app.py`
2. **Open browser**: Navigate to `http://localhost:5000`
3. **Select log type**: Choose "OFFICE_365" from the dropdown
4. **Load demo file**: Upload `OFFICE_365_demo.log` or use the existing `OFFICE_365.log`
5. **View patterns**: The three timestamp patterns will be automatically loaded
6. **Analyze**: Click analyze to see the regex matches highlighted with different colors

## Pattern Testing

You can test individual patterns by:

1. **CreationTime Pattern**: Should match every log entry (20 matches in demo file)
2. **LabelAppliedDateTime Pattern**: Should match entries with sensitivity label operations (3 matches in demo file)
3. **Sent Pattern**: Should match email-related entries (4 matches in demo file)

## Color Coding

Each pattern will be highlighted with a different color:
- **creation_time**: One color for the primary timestamp
- **label_applied**: Another color for label application timestamps  
- **sent**: A third color for email send timestamps

This helps visualize the different types of temporal data in Office 365 audit logs.

## Real-World Usage

These patterns are designed to extract timestamps from:
- **File operations** (access, download, upload, modify, delete)
- **Email activities** (send, receive, forward)
- **Collaboration events** (Teams messages, SharePoint access)
- **Security operations** (label application, role assignments)
- **Administrative actions** (user management, configuration changes)

The regex patterns account for the JSON structure of Office 365 audit logs and extract the timestamp values from the appropriate capture groups.