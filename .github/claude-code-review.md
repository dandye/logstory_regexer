# Claude Code Review Configuration

This repository uses Claude Code for automated PR reviews and code assistance via GitHub Actions.

## Setup

### Required Secrets

Add the following secrets to your GitHub repository settings:

1. `ANTHROPIC_API_KEY` - Your Anthropic API key for Claude access

### How It Works

The Claude Code action responds to:
- **Pull Requests** - Automatically triggers on PR creation and updates
- **@claude mentions** - Comment "@claude" in any PR or Issue to get help

### Usage Examples

**Request a code review:**
```
@claude please review this PR for security issues and performance problems
```

**Ask for help with implementation:**
```
@claude can you help implement error handling for the file upload feature?
```

**General questions:**
```
@claude explain how the regex pattern matching works in this code
```

## Configuration

The workflow is configured with:
- **Model**: Claude 3.5 Sonnet for high-quality analysis
- **Trigger**: "@claude" mentions in comments
- **Permissions**: Read code, write to PRs and issues
- **Environment**: Python 3.12 with project dependencies

## Customization

To modify the configuration, edit `.github/workflows/claude-code-review.yml`:

- Change `model` to use a different Claude model
- Modify `trigger_phrase` to use a different activation phrase
- Add additional workflow steps for specific project needs

## Manual Reviews

You can also use Claude Code directly:

1. Install Claude Code CLI: Follow instructions at [claude.ai/code](https://claude.ai/code)
2. Run terminal commands: `claude-code review <file>`
3. Use VS Code or JetBrains extensions for IDE integration