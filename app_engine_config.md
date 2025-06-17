# App Engine Configuration for User-Specific Storage

## Environment Variables Required

Add these to your App Engine deployment:

```yaml
# In app.yaml
env_variables:
  SECRET_KEY: "your-secure-secret-key-here"  # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
  GOOGLE_CLIENT_ID: "your-google-oauth-client-id.apps.googleusercontent.com"
  GCS_BUCKET_NAME: "your-project-id-user-files"  # Create this bucket in GCS
```

## Google Cloud Setup

1. **Enable Required APIs:**
   ```bash
   gcloud services enable storage-api.googleapis.com
   gcloud services enable iap.googleapis.com
   ```

2. **Create Storage Bucket:**
   ```bash
   gsutil mb -p YOUR_PROJECT_ID gs://YOUR_PROJECT_ID-user-files
   ```

3. **Set Bucket Permissions:**
   ```bash
   # Grant service account access to bucket
   gsutil iam ch serviceAccount:YOUR_SERVICE_ACCOUNT@appspot.gserviceaccount.com:objectAdmin gs://YOUR_PROJECT_ID-user-files
   ```

4. **Configure OAuth 2.0:**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Navigate to "APIs & Services" > "Credentials"
   - Create OAuth 2.0 Client ID
   - Add authorized JavaScript origins: `https://YOUR_PROJECT_ID.appspot.com`
   - Add authorized redirect URIs: `https://YOUR_PROJECT_ID.appspot.com/auth/google`
   - Copy the Client ID to use in GOOGLE_CLIENT_ID

## Security Implementation

The application implements multiple layers of security:

1. **Authentication:** Google Sign-In required for all file operations
2. **User Isolation:** Files stored in `/user-files/{user_hash}/` paths
3. **Access Control:** Every file operation verifies user ownership
4. **Signed URLs:** Time-limited access tokens for file downloads
5. **Session Security:** HTTPS-only cookies with CSRF protection

## Key Features

- **User-specific storage:** Each user's files are isolated in GCS
- **No cross-user access:** File paths include hashed user IDs
- **Metadata verification:** Files tagged with owner's user ID
- **Session-based access:** All API endpoints require authentication
- **Temporary URLs:** Files served via signed URLs, not direct access

## Testing Locally

1. Set environment variables:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
   export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
   export GCS_BUCKET_NAME="your-bucket-name"
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## Deployment

```bash
gcloud app deploy --project YOUR_PROJECT_ID
```

The application will automatically use the App Engine default service account for GCS access.