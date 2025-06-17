# Local Testing Instructions

## Quick Start (Without Google Cloud)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the local test server:**
   ```bash
   python local_test_setup.py
   ```

3. **Login locally:**
   - Visit http://localhost:5000/test-login
   - This creates a test session without needing Google OAuth

4. **Use the app:**
   - Go to http://localhost:5000
   - Upload and analyze log files (stored in memory during session)

## Testing with Real Google Cloud Storage

1. **Create a `.env` file:**
   ```bash
   cp .env.example .env
   ```

2. **Set up Google Cloud:**
   - Create a project in Google Cloud Console
   - Enable Cloud Storage API
   - Create a service account and download the JSON key
   - Create a storage bucket

3. **Configure `.env`:**
   ```env
   SECRET_KEY=your-generated-secret-key
   GOOGLE_CLIENT_ID=your-oauth-client-id.apps.googleusercontent.com
   GCS_BUCKET_NAME=your-bucket-name
   GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
   ```

4. **Set up OAuth for localhost:**
   - In Google Cloud Console > APIs & Services > Credentials
   - Edit your OAuth 2.0 Client ID
   - Add to Authorized JavaScript origins: `http://localhost:5000`
   - Add to Authorized redirect URIs: `http://localhost:5000/auth/google`

5. **Run the app:**
   ```bash
   python app.py
   ```

## Features to Test

- **Authentication:** Login/logout functionality
- **File Upload:** Upload log files (50MB limit)
- **User Isolation:** Files only accessible by uploader
- **Pattern Analysis:** Real-time regex visualization
- **File Persistence:** Files stored in GCS (if configured)

## Troubleshooting

- **"Could not initialize GCS client"**: This is normal for local testing without GCS credentials
- **Login issues**: Use `/test-login` for quick local testing
- **CORS errors**: Make sure SocketIO CORS is enabled (already configured)