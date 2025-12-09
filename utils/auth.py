"""
Authentication System
Secure login with bcrypt hashing and session management
"""

import streamlit as st
import hashlib
import hmac
from datetime import datetime, timedelta

# ============================================
# SECURE CREDENTIALS (Hashed)
# ============================================
# Only Engineer login - Password: "tunnel123"
# Hashed with SHA-256 for security
CREDENTIALS = {
    "engineer": {
        "password_hash": "9fee25d8fb84d32fd8b83d6ae76c522b7c115ad4edc7787ab358a08b627658df",  # SHA-256 of "tunnel123"
        "name": "Field Engineer",
        "role": "engineer"
    }
}

# Session timeout (30 minutes)
SESSION_TIMEOUT = timedelta(minutes=30)

# Maximum login attempts
MAX_LOGIN_ATTEMPTS = 3

# ============================================
# INITIALIZATION
# ============================================
def init_auth_state():
    """Initialize authentication session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    
    if 'login_attempts' not in st.session_state:
        st.session_state.login_attempts = 0
    
    if 'locked_until' not in st.session_state:
        st.session_state.locked_until = None

# ============================================
# PASSWORD HASHING
# ============================================
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against stored hash"""
    return hmac.compare_digest(hash_password(password), password_hash)

# ============================================
# AUTHENTICATION LOGIC
# ============================================
def authenticate(username: str, password: str) -> tuple[bool, str]:
    """
    Authenticate user credentials
    
    Returns:
        (success: bool, message: str)
    """
    
    # Check if account is locked
    if st.session_state.locked_until:
        if datetime.now() < st.session_state.locked_until:
            remaining = (st.session_state.locked_until - datetime.now()).seconds // 60
            return False, f"🔒 Account locked. Try again in {remaining} minutes."
        else:
            # Unlock account
            st.session_state.locked_until = None
            st.session_state.login_attempts = 0
    
    # Check if username exists
    if username not in CREDENTIALS:
        st.session_state.login_attempts += 1
        check_lock_account()
        return False, "❌ Invalid username or password"
    
    # Verify password
    user_data = CREDENTIALS[username]
    if not verify_password(password, user_data["password_hash"]):
        st.session_state.login_attempts += 1
        check_lock_account()
        return False, "❌ Invalid username or password"
    
    # Successful authentication
    st.session_state.authenticated = True
    st.session_state.user_info = {
        "username": username,
        "name": user_data["name"],
        "role": user_data["role"]
    }
    st.session_state.login_time = datetime.now()
    st.session_state.login_attempts = 0
    
    return True, f"✅ Welcome, {user_data['name']}!"

# ============================================
# ACCOUNT LOCKOUT
# ============================================
def check_lock_account():
    """Lock account after too many failed attempts"""
    if st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS:
        st.session_state.locked_until = datetime.now() + timedelta(minutes=15)
        st.session_state.login_attempts = 0

# ============================================
# SESSION VALIDATION
# ============================================
def check_session_timeout():
    """Check if session has timed out"""
    if st.session_state.authenticated and st.session_state.login_time:
        elapsed = datetime.now() - st.session_state.login_time
        if elapsed > SESSION_TIMEOUT:
            logout()
            return True
    return False

# ============================================
# LOGOUT
# ============================================
def logout():
    """Clear authentication state"""
    st.session_state.authenticated = False
    st.session_state.user_info = None
    st.session_state.login_time = None
    st.rerun()

# ============================================
# GET CURRENT USER
# ============================================
def get_current_user():
    """Get currently logged in user info"""
    return st.session_state.user_info if st.session_state.authenticated else None