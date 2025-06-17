#!/usr/bin/env python3
"""
User authentication and session management module.
Provides Google Sign-In integration and session handling.
"""
from flask import session, redirect, url_for, request
from functools import wraps
from google.oauth2 import id_token
from google.auth.transport import requests
import os

# Google OAuth2 configuration
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', 'not-set-for-local-testing')

def verify_google_token(token):
    """Verify the Google ID token and return user info."""
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        # Verify that the token was issued by Google
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        
        # Extract user information
        user_info = {
            'user_id': idinfo['sub'],  # Google's unique user ID
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', '')
        }
        
        return user_info
    except ValueError:
        # Invalid token
        return None

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user_id():
    """Get the current user's ID from session."""
    return session.get('user_id')

def get_current_user():
    """Get the current user's full information from session."""
    if 'user_id' in session:
        return {
            'user_id': session.get('user_id'),
            'email': session.get('email'),
            'name': session.get('name'),
            'picture': session.get('picture')
        }
    return None

def login_user(user_info):
    """Log in a user by storing their info in session."""
    session['user_id'] = user_info['user_id']
    session['email'] = user_info['email']
    session['name'] = user_info['name']
    session['picture'] = user_info['picture']
    session.permanent = True  # Make session persistent

def logout_user():
    """Log out the current user by clearing session."""
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('name', None)
    session.pop('picture', None)