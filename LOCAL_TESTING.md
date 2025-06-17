# Local Testing Options

You now have three ways to run the LogStory Regex Visualizer locally:

## 1. Simple Local Version (No Auth, No Cloud)

The easiest way to test - just like the original version:

```bash
# Install minimal dependencies
pip install -r requirements_local.txt

# Run the simple version
python local_app.py
```

- **URL**: http://localhost:5000
- **Features**: Full regex visualization, file uploads stored locally
- **No authentication required**
- **Files stored in**: `uploads/` directory

## 2. Local with Test Authentication

Test the full app with mock authentication:

```bash
# Install all dependencies
pip install -r requirements.txt

# Run with test login
python local_test_setup.py
```

- **Login**: Visit http://localhost:5000/test-login first
- **Then**: Go to http://localhost:5000
- **Features**: Full app with user sessions (files in memory)

## 3. Local with Real Google Cloud

For testing with actual Google Cloud Storage:

```bash
# Set up .env file
cp .env.example .env
# Edit .env with your credentials

# Run full app
python app.py
```

- **Requires**: Google Cloud credentials
- **Features**: Complete production functionality

## Quick Comparison

| Feature | local_app.py | local_test_setup.py | app.py |
|---------|--------------|---------------------|---------|
| Authentication | ❌ | ✅ (mock) | ✅ (Google) |
| Cloud Storage | ❌ | ❌ | ✅ |
| File Uploads | ✅ (local) | ✅ (memory) | ✅ (GCS) |
| Setup Complexity | Simple | Simple | Complex |
| Dependencies | Minimal | Full | Full |

Choose based on what you need to test!