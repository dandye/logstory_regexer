# Claude Code Review Configuration

This repository uses Claude Code for automated PR reviews to maintain code quality and catch potential issues early.

## Setup

### Required Secrets

Add the following secrets to your GitHub repository settings:

1. `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude access

### Configuration

The Claude Code review is configured to focus on:

- **Security vulnerabilities** - Identifying potential security issues
- **Performance issues** - Spotting performance bottlenecks
- **Code quality and best practices** - Ensuring clean, maintainable code
- **Python-specific improvements** - Python idioms and best practices
- **Flask/SocketIO specific concerns** - Framework-specific issues

### Excluded Files

The following files/directories are excluded from review:
- `venv/` - Virtual environment
- `uploads/` - Upload directory
- `*.png` - Image files
- `*.log` - Log files

## Customization

To modify the review configuration, edit `.github/workflows/claude-code-review.yml`:

- Change `review-level` to `basic` or `comprehensive`
- Modify `focus-areas` to add or remove review criteria
- Update `exclude-files` to change which files are ignored
- Adjust the `model` if you want to use a different Claude model

## Manual Reviews

You can also request manual Claude Code reviews by:

1. Installing Claude Code CLI: `pip install claude-code`
2. Running: `claude-code review <file-or-directory>`
3. Or using the web interface at [claude.ai/code](https://claude.ai/code)