"""
File Analysis Components
Single file and comparison analysis with your exact HDF5 processing logic
"""

import streamlit as st
import h5py
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
from utils.pdf_generator import generate_pdf_report

# ============================================
# YOUR ORIGINAL PROCESSING LOGIC (PRESERVED)
# ============================================

def process_bts_file(file_obj):
    """
    Process BTS HDF5 file - Supports both TempStrain and BrillFrequency files
    
    Args:
        file_obj: File object from Streamlit uploader
        
    Returns:
        dict: Contains time, strain, temperature, and distance data
    """
    try:
        # Open file from uploaded object
        with h5py.File(file_obj, "r") as f:
            # Navigate fixed path
            base_path = "Acquisition/Custom/Brillouin[0]/"
            
            # Read time data (always present)
            time = f[base_path + "BrillouinDataTime"][:]
            
            # Detect file type by checking which datasets exist
            has_strain = (base_path + "StrainData") in f
            has_temp = (base_path + "TemperatureData") in f
            has_freq = (base_path + "FrequencyData") in f
            has_amp = (base_path + "AmplitudeData") in f
            
            # Process TempStrain files
            if has_strain and has_temp:
                strain = f[base_path + "StrainData"][:]
                temp = f[base_path + "TemperatureData"][:]
                
                # Handle any number of rows (distance points)
                distance_points = strain.shape[1]
                distance = np.arange(distance_points)
                
                # Extract first sweep/frame
                strain_1 = strain[0]
                temp_1 = temp[0]
                
                return {
                    'success': True,
                    'file_type': 'TempStrain',
                    'time': time,
                    'strain_full': strain,
                    'temp_full': temp,
                    'strain_first': strain_1,
                    'temp_first': temp_1,
                    'distance': distance,
                    'distance_points': distance_points,
                    'metadata': {
                        'time_shape': time.shape,
                        'strain_shape': strain.shape,
                        'temp_shape': temp.shape
                    }
                }
            
            # Process BrillFrequency files
            elif has_freq and has_amp:
                freq = f[base_path + "FrequencyData"][:]
                amp = f[base_path + "AmplitudeData"][:]
                
                # Handle any number of rows (distance points)
                distance_points = freq.shape[1]
                distance = np.arange(distance_points)
                
                # Extract first sweep/frame
                freq_1 = freq[0]
                amp_1 = amp[0]
                
                return {
                    'success': True,
                    'file_type': 'BrillFrequency',
                    'time': time,
                    'freq_full': freq,
                    'amp_full': amp,
                    'freq_first': freq_1,
                    'amp_first': amp_1,
                    'distance': distance,
                    'distance_points': distance_points,
                    'metadata': {
                        'time_shape': time.shape,
                        'freq_shape': freq.shape,
                        'amp_shape': amp.shape
                    }
                }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file structure. Found: StrainData={has_strain}, TempData={has_temp}, FreqData={has_freq}, AmpData={has_amp}'
                }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# ============================================
# INTERACTIVE PLOTTING WITH PLOTLY
# ============================================

def create_plotly_chart(distance, data, title, ylabel, color='#667eea'):
    """Create interactive Plotly chart"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=distance,
        y=data,
        mode='lines',
        name=ylabel,
        line=dict(color=color, width=2),
        hovertemplate='<b>Distance</b>: %{x}<br><b>' + ylabel + '</b>: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, color='#333')),
        xaxis_title="Distance Index",
        yaxis_title=ylabel,
        template='plotly_white',
        hovermode='x unified',
        height=500,
        margin=dict(l=60, r=40, t=80, b=60)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
    
    return fig

# ============================================
# SINGLE FILE ANALYSIS
# ============================================

def show_single_file_analysis():
    """File analysis page"""
    
    st.subheader("File Analysis")
    st.markdown("Upload a BTS HDF5 file for Temperature and Strain analysis")
    
    # File upload
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose HDF5 File (.h5, .bts)",
            type=['h5', 'bts'],
            key='single_file',
            help="Upload DFOS Brillouin data file"
        )
    
    with col2:
        if uploaded_file:
            st.success("✅ File loaded")
            st.caption(f"**Name:** {uploaded_file.name}")
            st.caption(f"**Size:** {uploaded_file.size / 1024:.1f} KB")
    
    if uploaded_file is not None:
        
        # Process button
        if st.button("🔬 Process File", type="primary", use_container_width=True):
            
            with st.spinner("Processing file..."):
                result = process_bts_file(uploaded_file)
                
                if result['success']:
                    st.session_state.single_result = result
                    st.session_state.single_filename = uploaded_file.name
                    st.success("✅ File processed successfully!")
                    
                    # Add to history
                    if 'processing_history' not in st.session_state:
                        st.session_state.processing_history = []
                    
                    st.session_state.processing_history.append({
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Filename': uploaded_file.name,
                        'Type': 'Single Analysis',
                        'Distance Points': result['distance_points'],
                        'Status': 'Success'
                    })
                else:
                    st.error(f"❌ Error processing file: {result['error']}")
        
        # Display results if available
        if 'single_result' in st.session_state:
            result = st.session_state.single_result
            
            st.divider()
            
            # Show file type
            file_type_badge = "🌡️ Temperature & Strain" if result['file_type'] == 'TempStrain' else "📊 Frequency & Amplitude"
            st.info(f"**File Type:** {file_type_badge}")
            
            # Metadata
            with st.expander("📋 File Metadata", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Distance Points", result['distance_points'])
                with col2:
                    st.metric("Time Samples", len(result['time']))
                with col3:
                    if result['file_type'] == 'TempStrain':
                        st.metric("Data Shape", f"{result['metadata']['strain_shape']}")
                    else:
                        st.metric("Data Shape", f"{result['metadata']['freq_shape']}")
            
            st.divider()
            
            # Display plots based on file type
            if result['file_type'] == 'TempStrain':
                # Temperature Plot
                st.markdown("### 🌡️ Temperature Distribution")
                temp_fig = create_plotly_chart(
                    result['distance'],
                    result['temp_first'],
                    "Temperature vs Distance (First Sweep)",
                    "Temperature (°C)",
                    color='#e74c3c'
                )
                st.plotly_chart(temp_fig, use_container_width=True)
                
                # Strain Plot
                st.markdown("### 📏 Strain Distribution")
                strain_fig = create_plotly_chart(
                    result['distance'],
                    result['strain_first'],
                    "Strain vs Distance (First Sweep)",
                    "Strain (µε)",
                    color='#3498db'
                )
                st.plotly_chart(strain_fig, use_container_width=True)
            
            else:  # BrillFrequency
                # Frequency Plot
                st.markdown("### 📊 Brillouin Frequency Distribution")
                freq_fig = create_plotly_chart(
                    result['distance'],
                    result['freq_first'],
                    "Frequency vs Distance (First Sweep)",
                    "Frequency (GHz)",
                    color='#9b59b6'
                )
                st.plotly_chart(freq_fig, use_container_width=True)
                
                # Amplitude Plot
                st.markdown("### 📈 Brillouin Amplitude Distribution")
                amp_fig = create_plotly_chart(
                    result['distance'],
                    result['amp_first'],
                    "Amplitude vs Distance (First Sweep)",
                    "Amplitude (a.u.)",
                    color='#16a085'
                )
                st.plotly_chart(amp_fig, use_container_width=True)
            
            st.divider()
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📥 Download PDF Report", use_container_width=True):
                    pdf_bytes = generate_pdf_report(
                        result,
                        st.session_state.single_filename,
                        'single'
                    )
                    st.download_button(
                        label="💾 Save PDF",
                        data=pdf_bytes,
                        file_name=f"DFOS_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("📊 Export Data (CSV)", use_container_width=True):
                    # Create DataFrame based on file type
                    if result['file_type'] == 'TempStrain':
                        df = pd.DataFrame({
                            'Distance_Index': result['distance'],
                            'Temperature_C': result['temp_first'],
                            'Strain_uE': result['strain_first']
                        })
                    else:  # BrillFrequency
                        df = pd.DataFrame({
                            'Distance_Index': result['distance'],
                            'Frequency_GHz': result['freq_first'],
                            'Amplitude': result['amp_first']
                        })
                    
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="💾 Save CSV",
                        data=csv,
                        file_name=f"DFOS_Data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col3:
                if st.button("🔄 Reset", use_container_width=True):
                    del st.session_state.single_result
                    del st.session_state.single_filename
                    st.rerun()

# ============================================
# COMPARISON ANALYSIS (TWO FILES)
# ============================================

def show_comparison_analysis():
    """Compare two files side by side"""
    
    st.subheader("⚖️ Compare Two Files")
    st.markdown("Upload two BTS files for comparative analysis")
    
    # File uploads
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📁 File 1 (Baseline)")
        file1 = st.file_uploader(
            "Choose first HDF5 file",
            type=['h5', 'bts'],
            key='compare_file1'
        )
        if file1:
            st.success(f"✅ {file1.name}")
    
    with col2:
        st.markdown("#### 📁 File 2 (Comparison)")
        file2 = st.file_uploader(
            "Choose second HDF5 file",
            type=['h5', 'bts'],
            key='compare_file2'
        )
        if file2:
            st.success(f"✅ {file2.name}")
    
    # Process both files
    if file1 and file2:
        if st.button("🔬 Compare Files", type="primary", use_container_width=True):
            
            with st.spinner("Processing files..."):
                result1 = process_bts_file(file1)
                result2 = process_bts_file(file2)
                
                if result1['success'] and result2['success']:
                    st.session_state.compare_result1 = result1
                    st.session_state.compare_result2 = result2
                    st.session_state.compare_file1_name = file1.name
                    st.session_state.compare_file2_name = file2.name
                    st.success("✅ Both files processed successfully!")
                    
                    # Add to history
                    if 'processing_history' not in st.session_state:
                        st.session_state.processing_history = []
                    
                    st.session_state.processing_history.append({
                        'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Filename': f"{file1.name} vs {file2.name}",
                        'Type': 'Comparison',
                        'Distance Points': f"{result1['distance_points']} / {result2['distance_points']}",
                        'Status': 'Success'
                    })
                else:
                    error_msg = result1.get('error', '') or result2.get('error', '')
                    st.error(f"❌ Error: {error_msg}")
        
        # Display comparison results
        if 'compare_result1' in st.session_state:
            result1 = st.session_state.compare_result1
            result2 = st.session_state.compare_result2
            
            st.divider()
            
            # Comparison metrics
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"#### 📊 {st.session_state.compare_file1_name}")
                st.metric("Distance Points", result1['distance_points'])
            with col2:
                st.markdown(f"#### 📊 {st.session_state.compare_file2_name}")
                st.metric("Distance Points", result2['distance_points'])
            
            st.divider()
            
            # Temperature Comparison
            st.markdown("### 🌡️ Temperature Comparison")
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=result1['distance'],
                y=result1['temp_first'],
                mode='lines',
                name='File 1',
                line=dict(color='#e74c3c', width=2)
            ))
            fig_temp.add_trace(go.Scatter(
                x=result2['distance'],
                y=result2['temp_first'],
                mode='lines',
                name='File 2',
                line=dict(color='#f39c12', width=2, dash='dash')
            ))
            fig_temp.update_layout(
                title="Temperature Comparison",
                xaxis_title="Distance Index",
                yaxis_title="Temperature (°C)",
                template='plotly_white',
                height=500
            )
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # Strain Comparison
            st.markdown("### 📏 Strain Comparison")
            fig_strain = go.Figure()
            fig_strain.add_trace(go.Scatter(
                x=result1['distance'],
                y=result1['strain_first'],
                mode='lines',
                name='File 1',
                line=dict(color='#3498db', width=2)
            ))
            fig_strain.add_trace(go.Scatter(
                x=result2['distance'],
                y=result2['strain_first'],
                mode='lines',
                name='File 2',
                line=dict(color='#9b59b6', width=2, dash='dash')
            ))
            fig_strain.update_layout(
                title="Strain Comparison",
                xaxis_title="Distance Index",
                yaxis_title="Strain (µε)",
                template='plotly_white',
                height=500
            )
            st.plotly_chart(fig_strain, use_container_width=True)
            
            # Difference Analysis
            st.divider()
            st.markdown("### 📊 Difference Analysis")
            
            if result1['distance_points'] == result2['distance_points']:
                temp_diff = result2['temp_first'] - result1['temp_first']
                strain_diff = result2['strain_first'] - result1['strain_first']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Max Temp Difference", f"{np.max(np.abs(temp_diff)):.2f} °C")
                    st.metric("Mean Temp Difference", f"{np.mean(temp_diff):.2f} °C")
                with col2:
                    st.metric("Max Strain Difference", f"{np.max(np.abs(strain_diff)):.2f} µε")
                    st.metric("Mean Strain Difference", f"{np.mean(strain_diff):.2f} µε")
            else:
                st.warning("⚠️ Files have different distance points. Difference analysis requires matching dimensions.")
            
            st.divider()
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📥 Download Comparison Report", use_container_width=True):
                    pdf_bytes = generate_pdf_report(
                        (result1, result2),
                        (st.session_state.compare_file1_name, st.session_state.compare_file2_name),
                        'comparison'
                    )
                    st.download_button(
                        label="💾 Save PDF",
                        data=pdf_bytes,
                        file_name=f"DFOS_Comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            
            with col2:
                if st.button("🔄 Reset Comparison", use_container_width=True):
                    for key in ['compare_result1', 'compare_result2', 'compare_file1_name', 'compare_file2_name']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()