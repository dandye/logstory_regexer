#!/usr/bin/env python3
"""
Local testing setup script for LogStory Regex Visualizer
This helps you test with mock authentication locally
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create a modified app for local testing
from app import app, socketio
from auth import login_user

# Add a test login route for local development
@app.route('/test-login')
def test_login():
    """Quick login for local testing without Google OAuth"""
    # Create a test user
    test_user = {
        'user_id': 'test-user-123',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': ''
    }
    login_user(test_user)
    return '''
    <html>
    <body>
        <h1>Test Login Successful</h1>
        <p>You are now logged in as: test@example.com</p>
        <a href="/">Go to main app</a>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("\n" + "="*50)
    print("LOCAL TESTING MODE")
    print("="*50)
    print("\nFor local testing without Google OAuth:")
    print("1. Visit http://localhost:5000/test-login")
    print("2. Then go to http://localhost:5000")
    print("\nFor testing with real Google OAuth:")
    print("1. Set up OAuth credentials for http://localhost:5000")
    print("2. Visit http://localhost:5000/login")
    print("\n" + "="*50 + "\n")
    
    socketio.run(app, debug=True, port=5000)