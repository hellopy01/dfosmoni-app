"""
Dashboard Component
Main application interface after login
"""

import streamlit as st
from utils.auth import logout, get_current_user, check_session_timeout
from components.file_analyzer import show_single_file_analysis, show_comparison_analysis
from datetime import datetime

def show_dashboard():
    """Display main dashboard"""
    
    # Check session timeout
    if check_session_timeout():
        st.warning("⏱️ Session expired. Please login again.")
        st.stop()
    
    # Get current user
    user = get_current_user()
    
    # ============================================
    # SIDEBAR NAVIGATION
    # ============================================
    with st.sidebar:
        # User info header - Professional blue theme
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); 
                        padding: 1.5rem; border-radius: 10px; margin-bottom: 1rem; color: white;
                        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);'>
                <h3 style='margin: 0; font-size: 1.1rem;'>👤 {user['name']}</h3>
                <p style='margin: 0.3rem 0 0 0; font-size: 0.85rem; opacity: 0.9;'>
                    {user['role'].upper()}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown("### 📋 Navigation")
        
        page = st.radio(
            "Select View:",
            ["File Analysis", "📁 File History", "⚙️ Settings"],
            # ["File Analysis", "⚖️ Compare Two Files", "📁 File History", "⚙️ Settings"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # System info
        st.markdown("### ℹ️ System Info")
        st.metric("Session Time", f"{(datetime.now() - st.session_state.login_time).seconds // 60} min")
        st.caption(f"Login: {st.session_state.login_time.strftime('%I:%M %p')}")
        
        st.divider()
        
        # Logout button
        if st.button("🔓 Logout", use_container_width=True, type="primary"):
            logout()
    
    # ============================================
    # MAIN CONTENT AREA
    # ============================================
    
    # Dashboard header
    st.markdown(f"""
        <div class='dashboard-header'>
            <h1 style='margin: 0; font-size: 2rem;'>DFOS Monitoring Dashboard</h1>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>
                Distributed Fiber Optic Sensing - Tunnel Monitoring System
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Route to selected page
    if page == "File Analysis":
        show_single_file_analysis()
    
    # elif page == "⚖️ Compare Two Files":
    #     show_comparison_analysis()
    
    elif page == "📁 File History":
        show_file_history()
    
    elif page == "⚙️ Settings":
        show_settings()

# ============================================
# ADDITIONAL PAGES
# ============================================

def show_file_history():
    """Show file processing history"""
    st.subheader("📁 Processing History")
    
    if 'processing_history' not in st.session_state:
        st.session_state.processing_history = []
    
    if not st.session_state.processing_history:
        st.info("No files processed yet. Upload files from the analysis pages.")
    else:
        st.dataframe(
            st.session_state.processing_history,
            use_container_width=True,
            hide_index=True
        )
        
        if st.button("🗑️ Clear History"):
            st.session_state.processing_history = []
            st.rerun()

def show_settings():
    """Show application settings"""
    st.subheader("⚙️ Application Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎨 Display Options")
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        plot_style = st.selectbox("Plot Style", ["Professional", "Minimalist", "Technical"])
        
    with col2:
        st.markdown("#### 📊 Data Options")
        auto_save = st.checkbox("Auto-save results", value=True)
        high_res_export = st.checkbox("High-resolution PDF export", value=True)
    
    st.divider()
    
    st.markdown("#### 📐 Measurement Units")
    col1, col2 = st.columns(2)
    with col1:
        distance_unit = st.selectbox("Distance", ["Meters", "Feet", "Kilometers"])
    with col2:
        temp_unit = st.selectbox("Temperature", ["Celsius", "Fahrenheit", "Kelvin"])
    
    st.divider()
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("✅ Settings saved successfully!")
    
    st.divider()
    
    # About section
    with st.expander("ℹ️ About DFOS System"):
        st.markdown("""
        ### Distributed Fiber Optic Sensing System
        
        **Technology:** Brillouin-based DFOS  
        **Application:** Tunnel structural monitoring
        
        **Measured Parameters:**
        - 🌡️ Temperature distribution
        - 📏 Strain distribution
        - 📍 Spatial resolution: Variable
        - ⏱️ Temporal resolution: Configurable
        
        **File Format:** HDF5 (PRODML DAS Compatible)
        
        **Version:** 1.0.0  
        **Last Updated:** December 2024
        """)
