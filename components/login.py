"""
Login Page Component
Professional authentication interface
"""

import streamlit as st
from utils.auth import authenticate

def show_login_page():
    """Display the login page"""
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # App Logo/Header - Clean professional design
        st.markdown("""
            <div style='text-align: center; padding: 2rem 0 1rem 0;'>
                <h1 style='color: #1e40af; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 700;'>
                    🔬 DFOS Monitoring
                </h1>
                <p style='color: #475569; font-size: 1rem; margin: 0;'>
                    Distributed Fiber Optic Sensing System
                </p>
                <p style='color: #64748b; font-size: 0.875rem; margin-top: 0.25rem;'>
                    Tunnel Strain & Temperature Monitoring
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Login container
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            
            # Login form header - Clean and simple
            st.markdown("""
                <h2 style='text-align: center; color: #1e293b; margin-bottom: 2rem; font-weight: 600; font-size: 1.5rem;'>
                    Sign In
                </h2>
            """, unsafe_allow_html=True)
            
            # Check for locked account message
            if st.session_state.locked_until:
                st.error("🔒 Too many failed attempts. Account temporarily locked.")
                if st.button("🔄 Reset Lock (Emergency)", type="secondary", use_container_width=True):
                    st.session_state.locked_until = None
                    st.session_state.login_attempts = 0
                    st.success("✅ Lock reset! Please try again.")
                    st.rerun()
            
            # Login form
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "Username",
                    placeholder="Enter your username",
                    key="login_username",
                    label_visibility="visible"
                )
                
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                    key="login_password",
                    label_visibility="visible"
                )
                
                # Remember me checkbox
                remember_me = st.checkbox("Remember me", key="remember_me")
                
                # Submit button
                submit = st.form_submit_button("🔐 Login", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("⚠️ Please enter both username and password")
                    else:
                        success, message = authenticate(username, password)
                        
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                            remaining_attempts = 3 - st.session_state.login_attempts
                            if remaining_attempts > 0 and not st.session_state.locked_until:
                                st.warning(f"⚠️ {remaining_attempts} attempts remaining")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Footer - Clean and professional
            st.markdown("""
                <div style='text-align: center; margin-top: 2rem; color: #64748b; font-size: 0.875rem;'>
                    <p>© 2024 DFOS Monitoring System | Secure Access</p>
                    <p style='margin-top: 0.5rem; color: #94a3b8;'>
                        🔒 All connections are encrypted
                    </p>
                </div>
            """, unsafe_allow_html=True)
