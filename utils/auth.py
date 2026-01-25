"""
Authentication utilities for Google OAuth
Handles login, logout, session management, and user profile
"""
import streamlit as st
import sqlite3
import os
from datetime import datetime
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests
import json

# Try to import from config_secrets first, fallback to st.secrets
try:
    from config_secrets import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI
    # Only allow HTTP for local development
    if 'localhost' in GOOGLE_REDIRECT_URI:
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
except ImportError:
    # Using Streamlit secrets (production)
    try:
        GOOGLE_CLIENT_ID = st.secrets["google_oauth"]["client_id"]
        GOOGLE_CLIENT_SECRET = st.secrets["google_oauth"]["client_secret"]
        GOOGLE_REDIRECT_URI = st.secrets["google_oauth"]["redirect_uri"]
        # Only allow HTTP for localhost in production secrets
        if 'localhost' in GOOGLE_REDIRECT_URI:
            os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    except Exception:
        # Secrets not configured - set defaults for development
        GOOGLE_CLIENT_ID = ""
        GOOGLE_CLIENT_SECRET = ""
        GOOGLE_REDIRECT_URI = "http://localhost:8501"
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


# OAuth 2.0 scopes
SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('edulytix.db', check_same_thread=False)


def init_session_state():
    """Initialize session state variables for authentication"""
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False


def create_oauth_flow():
    """Create Google OAuth flow"""
    client_config = {
        "web": {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [GOOGLE_REDIRECT_URI]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI
    )
    
    return flow


def get_authorization_url():
    """Get Google OAuth authorization URL"""
    flow = create_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    # Store state in session for CSRF protection
    st.session_state.oauth_state = state
    
    return authorization_url


def handle_oauth_callback(authorization_response):
    """
    Handle OAuth callback and exchange code for token
    Returns user info dict or None if failed
    """
    try:
        flow = create_oauth_flow()
        
        # Fetch token from authorization response
        flow.fetch_token(authorization_response=authorization_response)
        
        # Get credentials
        credentials = flow.credentials
        
        # Verify the token and get user info
        request = requests.Request()
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            request,
            GOOGLE_CLIENT_ID
        )
        
        # Extract user information
        user_info = {
            'google_id': id_info.get('sub'),
            'email': id_info.get('email'),
            'name': id_info.get('name'),
            'profile_picture': id_info.get('picture'),
            'email_verified': id_info.get('email_verified', False)
        }
        
        return user_info
        
    except Exception as e:
        # Log error but don't show full traceback in production
        st.error(f"OAuth callback error: {str(e)}")
        # Only show traceback if in development
        if 'localhost' in GOOGLE_REDIRECT_URI:
            import traceback
            st.code(traceback.format_exc())
        return None


def create_or_update_user(user_info):
    """
    Create new user or update existing user in database
    Returns user_id
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # List of admin emails
    ADMIN_EMAILS = [
        'tirthdhara108@gmail.com',
        'tirth.shah@tamu.edu'
    ]
    
    try:
        # Check if user exists
        cursor.execute('SELECT user_id FROM users WHERE google_id = ?', (user_info['google_id'],))
        existing_user = cursor.fetchone()
        
        # Determine role based on email
        role = 'admin' if user_info['email'] in ADMIN_EMAILS else 'user'
        
        if existing_user:
            # Update existing user
            cursor.execute('''
                UPDATE users 
                SET name = ?, 
                    profile_picture_url = ?, 
                    last_login = ?,
                    role = ?
                WHERE google_id = ?
            ''', (
                user_info['name'],
                user_info['profile_picture'],
                datetime.now(),
                role,
                user_info['google_id']
            ))
            user_id = existing_user[0]
        else:
            # Create new user with appropriate role
            cursor.execute('''
                INSERT INTO users (google_id, email, name, profile_picture_url, role, created_at, last_login)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_info['google_id'],
                user_info['email'],
                user_info['name'],
                user_info['profile_picture'],
                role,
                datetime.now(),
                datetime.now()
            ))
            user_id = cursor.lastrowid
        
        conn.commit()
        return user_id
        
    except Exception as e:
        conn.rollback()
        st.error(f"Database error: {str(e)}")
        return None
    
    finally:
        conn.close()


def get_user_by_id(user_id):
    """Get user information from database by user_id"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT user_id, google_id, email, name, profile_picture_url, created_at, last_login
            FROM users
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        
        row = cursor.fetchone()
        
        if row:
            return {
                'user_id': row[0],
                'google_id': row[1],
                'email': row[2],
                'name': row[3],
                'profile_picture': row[4],
                'created_at': row[5],
                'last_login': row[6]
            }
        
        return None
        
    finally:
        conn.close()


def login_user(user_info):
    """
    Login user and store in session
    Returns True if successful, False otherwise
    """
    user_id = create_or_update_user(user_info)
    
    if user_id:
        # Store user info in session
        st.session_state.user = {
            'user_id': user_id,
            'google_id': user_info['google_id'],
            'email': user_info['email'],
            'name': user_info['name'],
            'profile_picture': user_info['profile_picture']
        }
        st.session_state.authenticated = True
        return True
    
    return False


def logout_user():
    """Logout user and clear session"""
    st.session_state.user = None
    st.session_state.authenticated = False
    if 'oauth_state' in st.session_state:
        del st.session_state.oauth_state


def is_authenticated():
    """Check if user is authenticated"""
    return st.session_state.get('authenticated', False)


def get_current_user():
    """Get current logged-in user info"""
    return st.session_state.get('user', None)


def require_auth(feature_name="this feature"):
    """
    Decorator/helper to require authentication for a feature
    Shows login prompt if not authenticated
    Returns True if authenticated, False otherwise
    """
    if not is_authenticated():
        st.warning(f"🔒 Please sign in to use {feature_name}")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔐 Sign in with Google", use_container_width=True, type="primary"):
                auth_url = get_authorization_url()
                st.markdown(f'<meta http-equiv="refresh" content="0;url={auth_url}">', unsafe_allow_html=True)
        
        return False
    
    return True


def is_admin():
    """Check if current user has admin role"""
    if not is_authenticated():
        return False
    
    user = get_current_user()
    if not user:
        return False
    
    # Check role in database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT role FROM users WHERE user_id = ?', (user['user_id'],))
        result = cursor.fetchone()
        
        if result and result[0] == 'admin':
            return True
        
        return False
        
    finally:
        conn.close()


def get_user_role():
    """Get current user's role"""
    if not is_authenticated():
        return None
    
    user = get_current_user()
    if not user:
        return None
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT role FROM users WHERE user_id = ?', (user['user_id'],))
        result = cursor.fetchone()
        
        return result[0] if result else 'user'
        
    finally:
        conn.close()
