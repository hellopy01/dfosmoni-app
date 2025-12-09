"""
DFOS Monitoring System - Main Application
Professional Tunnel Monitoring with Secure Authentication
"""

import streamlit as st
from components.login import show_login_page
from components.dashboard import show_dashboard
from utils.auth import init_auth_state

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="DFOS Monitoring System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar on login page
)

# ============================================
# CUSTOM CSS FOR PROFESSIONAL LOOK
# ============================================
def load_css():
    st.markdown("""
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Professional white/blue background */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Login container styling - Clean white card */
    .login-container {
        background: white;
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        max-width: 450px;
        margin: 3rem auto;
        border: 1px solid #e0e7ff;
    }
    
    /* Dashboard styling - Professional blue */
    .dashboard-header {
        background: linear-gradient(90deg, #2563eb 0%, #1e40af 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }
    
    /* Button styling - Professional blue */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.3);
        background: linear-gradient(90deg, #1d4ed8 0%, #1e40af 100%);
    }
    
    /* File uploader styling */
    .uploadedFile {
        border: 2px dashed #2563eb;
        border-radius: 10px;
        padding: 1rem;
        background: #eff6ff;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border: 1px solid #e0e7ff;
    }
    
    /* Input fields styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        border: 1px solid #cbd5e1;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #2563eb;
        box-shadow: 0 0 0 1px #2563eb;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# INITIALIZE APPLICATION
# ============================================
def main():
    """Main application entry point"""
    
    # Load custom CSS
    load_css()
    
    # Initialize authentication state
    init_auth_state()
    
    # Route to appropriate page based on authentication status
    if st.session_state.authenticated:
        show_dashboard()
    else:
        show_login_page()

# ============================================
# RUN APPLICATION
# ============================================
if __name__ == "__main__":
    main()
