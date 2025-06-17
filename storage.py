#!/usr/bin/env python3
"""
Google Cloud Storage integration for user-specific file storage.
Handles file uploads, downloads, and access control.
"""
from google.cloud import storage
from datetime import timedelta
import os
import hashlib

# Initialize storage client (handle local testing)
try:
    storage_client = storage.Client()
except Exception as e:
    print(f"Warning: Could not initialize GCS client: {e}")
    print("Using mock storage for local testing")
    storage_client = None

# Get bucket name from environment variable
BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', 'logstory-user-files')

def get_user_storage_path(user_id, filename):
    """
    Generate a secure storage path for a user's file.
    Uses user ID to create isolated storage spaces.
    """
    # Hash the user ID for additional security
    user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:16]
    return f"user-files/{user_hash}/{filename}"

def upload_file_to_gcs(file_content, user_id, filename, content_type='text/plain'):
    """
    Upload a file to Google Cloud Storage in the user's folder.
    
    Args:
        file_content: File content as bytes or file-like object
        user_id: User's unique identifier
        filename: Original filename (will be sanitized)
        content_type: MIME type of the file
        
    Returns:
        dict: Upload result with GCS path and signed URL
    """
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        
        # Generate secure path
        blob_path = get_user_storage_path(user_id, filename)
        blob = bucket.blob(blob_path)
        
        # Set metadata
        blob.metadata = {
            'user_id': user_id,
            'original_filename': filename,
            'upload_timestamp': str(os.times())
        }
        
        # Upload file
        if hasattr(file_content, 'read'):
            blob.upload_from_file(file_content, content_type=content_type)
        else:
            blob.upload_from_string(file_content, content_type=content_type)
        
        # Generate a signed URL for temporary access (1 hour)
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=1),
            method="GET"
        )
        
        return {
            'success': True,
            'gcs_path': blob_path,
            'signed_url': signed_url,
            'filename': filename
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_file_from_gcs(user_id, filename):
    """
    Retrieve a file from GCS if the user has access.
    
    Args:
        user_id: User's unique identifier
        filename: Filename to retrieve
        
    Returns:
        dict: File content and metadata or error
    """
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob_path = get_user_storage_path(user_id, filename)
        blob = bucket.blob(blob_path)
        
        # Check if file exists
        if not blob.exists():
            return {
                'success': False,
                'error': 'File not found'
            }
        
        # Verify ownership through metadata
        blob.reload()
        if blob.metadata and blob.metadata.get('user_id') != user_id:
            return {
                'success': False,
                'error': 'Access denied'
            }
        
        # Download content
        content = blob.download_as_text()
        
        return {
            'success': True,
            'content': content,
            'filename': filename,
            'metadata': blob.metadata
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def generate_signed_url(user_id, filename, expiration_hours=1):
    """
    Generate a signed URL for temporary file access.
    
    Args:
        user_id: User's unique identifier
        filename: Filename to generate URL for
        expiration_hours: Hours until URL expires
        
    Returns:
        str: Signed URL or None if error
    """
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob_path = get_user_storage_path(user_id, filename)
        blob = bucket.blob(blob_path)
        
        # Verify file exists and user owns it
        if not blob.exists():
            return None
            
        blob.reload()
        if blob.metadata and blob.metadata.get('user_id') != user_id:
            return None
        
        # Generate signed URL
        signed_url = blob.generate_signed_url(
            version="v4",
            expiration=timedelta(hours=expiration_hours),
            method="GET"
        )
        
        return signed_url
        
    except Exception:
        return None

def delete_user_file(user_id, filename):
    """
    Delete a user's file from GCS.
    
    Args:
        user_id: User's unique identifier
        filename: Filename to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob_path = get_user_storage_path(user_id, filename)
        blob = bucket.blob(blob_path)
        
        # Verify ownership before deletion
        if blob.exists():
            blob.reload()
            if blob.metadata and blob.metadata.get('user_id') == user_id:
                blob.delete()
                return True
                
        return False
        
    except Exception:
        return False

def list_user_files(user_id):
    """
    List all files belonging to a user.
    
    Args:
        user_id: User's unique identifier
        
    Returns:
        list: List of file information dictionaries
    """
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        prefix = f"user-files/{user_hash}/"
        
        files = []
        for blob in bucket.list_blobs(prefix=prefix):
            # Extract filename from path
            filename = blob.name.replace(prefix, '')
            if filename:  # Skip the folder itself
                files.append({
                    'filename': filename,
                    'size': blob.size,
                    'created': blob.time_created,
                    'updated': blob.updated,
                    'content_type': blob.content_type
                })
        
        return files
        
    except Exception:
        return []