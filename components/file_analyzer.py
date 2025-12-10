"""
File Analysis Components - COMPLETE WITH MULTIPLE FILE UPLOAD
Fixed: Added missing export functions and corrected offset logic
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
                    'error': 'Unknown file format. File must contain either (StrainData + TemperatureData) or (FrequencyData + AmplitudeData)'
                }
                
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# ============================================
# EXPORT FUNCTIONS
# ============================================

def export_to_csv(distance, temp, strain):
    """Export TempStrain data to CSV"""
    df = pd.DataFrame({
        'Distance_Index': distance,
        'Temperature_C': temp,
        'Strain_ue': strain
    })
    return df.to_csv(index=False)

def export_to_csv_brillouin(distance, freq, amp):
    """Export BrillFrequency data to CSV"""
    df = pd.DataFrame({
        'Distance_Index': distance,
        'Frequency_GHz': freq,
        'Amplitude': amp
    })
    return df.to_csv(index=False)

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
# MULTIPLE FILE ANALYSIS
# ============================================

def show_single_file_analysis():
    """Multiple File Analysis with individual and batch processing"""
    
    st.markdown("## 📁 Multiple File Analysis")
    
    # Initialize session state
    if 'num_upload_slots' not in st.session_state:
        st.session_state.num_upload_slots = 1
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = {}
    
    # Upload section header
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("### 📤 Upload Files")
        st.caption("Add multiple files for analysis")
    with col2:
        if st.button("➕ Add Slot", type="primary", use_container_width=True):
            st.session_state.num_upload_slots += 1
            st.rerun()
    
    st.divider()
    
    # Track uploaded files
    uploaded_files_dict = {}
    
    # Display upload slots
    for i in range(st.session_state.num_upload_slots):
        with st.container():
            cols = st.columns([5, 2, 1])
            
            with cols[0]:
                uploaded = st.file_uploader(
                    f"File Slot {i+1}",
                    type=['h5', 'bts'],
                    key=f"upload_slot_{i}",
                    label_visibility="collapsed"
                )
                if uploaded:
                    uploaded_files_dict[f"slot_{i}"] = {
                        'file': uploaded,
                        'name': uploaded.name,
                        'size': uploaded.size
                    }
            
            with cols[1]:
                if uploaded:
                    if st.button(f"🔍 Process", key=f"process_{i}", use_container_width=True):
                        with st.spinner(f"Processing {uploaded.name}..."):
                            try:
                                result = process_bts_file(uploaded)
                                if result['success']:
                                    st.session_state.processed_files[uploaded.name] = result
                                    st.success(f"✅ Done")
                                    st.rerun()
                                else:
                                    st.error(f"❌ {result.get('error', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"❌ {str(e)[:50]}")
            
            with cols[2]:
                if st.button("🗑️", key=f"remove_slot_{i}", help="Remove this slot"):
                    # Remove from processed files if exists
                    if uploaded and uploaded.name in st.session_state.processed_files:
                        del st.session_state.processed_files[uploaded.name]
                    # Decrease slot count (minimum 1)
                    st.session_state.num_upload_slots = max(1, st.session_state.num_upload_slots - 1)
                    st.rerun()
    
    # Batch processing section
    if uploaded_files_dict:
        st.divider()
        cols = st.columns([2, 2, 2])
        with cols[0]:
            st.metric("📁 Files Added", len(uploaded_files_dict))
        with cols[1]:
            st.metric("✅ Processed", len(st.session_state.processed_files))
        with cols[2]:
            if st.button("🚀 Process All", type="primary", use_container_width=True):
                progress = st.progress(0)
                status = st.empty()
                total = len(uploaded_files_dict)
                
                for idx, (slot_id, file_info) in enumerate(uploaded_files_dict.items()):
                    fname = file_info['name']
                    
                    # Skip if already processed
                    if fname in st.session_state.processed_files:
                        continue
                    
                    status.text(f"Processing {fname}...")
                    
                    try:
                        result = process_bts_file(file_info['file'])
                        if result['success']:
                            st.session_state.processed_files[fname] = result
                    except Exception as e:
                        st.error(f"❌ {fname}: {str(e)[:30]}")
                    
                    progress.progress((idx + 1) / total)
                
                status.text("✅ All files processed!")
                st.rerun()
    
    # Display results
    if st.session_state.processed_files:
        st.divider()
        st.markdown("## 📊 Analysis Results")
        
        # Clear all button
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                st.session_state.processed_files = {}
                st.rerun()
        
        # Show each file's results
        for filename, result in list(st.session_state.processed_files.items()):
            st.markdown("---")
            
            # File header
            cols = st.columns([5, 1])
            with cols[0]:
                emoji = "🌡️" if result['file_type'] == 'TempStrain' else "📡"
                st.markdown(f"### {emoji} **{filename}**")
                st.caption(f"📊 Type: **{result['file_type']}** | Distance Points: **{result['distance_points']}** | Time Samples: **{len(result['time'])}**")
            with cols[1]:
                if st.button("❌ Remove", key=f"del_{filename}", help="Remove this file", use_container_width=True):
                    del st.session_state.processed_files[filename]
                    st.rerun()
            
            # Create unique file ID (clean filename for keys)
            file_id = filename.replace('.', '_').replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
            
            # Initialize reset counters for this file
            for plot_type in ['temp', 'strain', 'freq', 'amp']:
                key = f'{plot_type}_reset_{file_id}'
                if key not in st.session_state:
                    st.session_state[key] = 0
            
            # Export options
            with st.expander("📥 Export Options", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV Export
                    if result['file_type'] == 'TempStrain':
                        csv_data = export_to_csv(result['distance'], result['temp_first'], result['strain_first'])
                    else:
                        csv_data = export_to_csv_brillouin(result['distance'], result['freq_first'], result['amp_first'])
                    
                    st.download_button(
                        "📄 Download CSV",
                        csv_data,
                        f"{filename}_analysis.csv",
                        "text/csv",
                        key=f"csv_{file_id}",
                        use_container_width=True
                    )
                
                with col2:
                    # PDF Export
                    if st.button("📥 Generate PDF", key=f"pdf_btn_{file_id}", use_container_width=True):
                        with st.spinner("Generating PDF..."):
                            try:
                                pdf_bytes = generate_pdf_report(result, filename, 'single')
                                st.download_button(
                                    "⬇️ Download PDF",
                                    pdf_bytes,
                                    f"{filename}_report.pdf",
                                    "application/pdf",
                                    key=f"pdf_dl_{file_id}",
                                    use_container_width=True
                                )
                            except Exception as e:
                                st.error(f"PDF generation failed: {str(e)}")
            
            # Display plots based on file type
            if result['file_type'] == 'TempStrain':
                # ============================================
                # TEMPERATURE PLOT
                # ============================================
                st.markdown(f"#### 🌡️ Temperature - {filename}")
                
                # Reset button
                if st.button(f"🔄 Reset Temperature", key=f"rst_temp_{file_id}", type="secondary"):
                    st.session_state[f'temp_reset_{file_id}'] += 1
                    st.rerun()
                
                # Controls
                with st.expander("⚙️ Temperature Controls", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    reset_count = st.session_state[f'temp_reset_{file_id}']
                    
                    with c1:
                        # FIXED: Changed to negative step for subtraction by default
                        t_off = st.number_input(
                            "Y-Axis Offset (°C)",
                            value=0.0,
                            step=0.1,
                            format="%.2f",
                            key=f"toff_{file_id}_{reset_count}",
                            help="Positive = Add, Negative = Subtract"
                        )
                    with c2:
                        t_min = st.number_input(
                            "X-Axis Min",
                            value=0,
                            min_value=0,
                            max_value=int(result['distance_points']-1),
                            key=f"tmin_{file_id}_{reset_count}"
                        )
                    with c3:
                        t_max = st.number_input(
                            "X-Axis Max",
                            value=int(result['distance_points']-1),
                            min_value=int(t_min + 1),
                            max_value=int(result['distance_points']-1),
                            key=f"tmax_{file_id}_{reset_count}"
                        )
                
                # Apply offset and filter
                temp_data = result['temp_first'] + t_off
                mask = (result['distance'] >= t_min) & (result['distance'] <= t_max)
                
                # Show status
                st.caption(f"📊 Range: {t_min} to {t_max} | Y-Offset: {t_off:+.2f}°C | Showing {int(mask.sum())} points")
                
                # Create and display plot
                fig_temp = create_plotly_chart(
                    result['distance'][mask],
                    temp_data[mask],
                    f"Temperature - {filename} (Offset: {t_off:+.2f}°C)",
                    "Temperature (°C)",
                    '#e74c3c'
                )
                st.plotly_chart(fig_temp, use_container_width=True, key=f"tplot_{file_id}_{reset_count}")
                
                # ============================================
                # STRAIN PLOT
                # ============================================
                st.markdown(f"#### 📏 Strain - {filename}")
                
                # Reset button
                if st.button(f"🔄 Reset Strain", key=f"rst_strain_{file_id}", type="secondary"):
                    st.session_state[f'strain_reset_{file_id}'] += 1
                    st.rerun()
                
                # Controls
                with st.expander("⚙️ Strain Controls", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    reset_count = st.session_state[f'strain_reset_{file_id}']
                    
                    with c1:
                        s_off = st.number_input(
                            "Y-Axis Offset (µε)",
                            value=0.0,
                            step=1.0,
                            format="%.2f",
                            key=f"soff_{file_id}_{reset_count}",
                            help="Positive = Add, Negative = Subtract"
                        )
                    with c2:
                        s_min = st.number_input(
                            "X-Axis Min",
                            value=0,
                            min_value=0,
                            max_value=int(result['distance_points']-1),
                            key=f"smin_{file_id}_{reset_count}"
                        )
                    with c3:
                        s_max = st.number_input(
                            "X-Axis Max",
                            value=int(result['distance_points']-1),
                            min_value=int(s_min + 1),
                            max_value=int(result['distance_points']-1),
                            key=f"smax_{file_id}_{reset_count}"
                        )
                
                # Apply offset and filter
                strain_data = result['strain_first'] + s_off
                mask = (result['distance'] >= s_min) & (result['distance'] <= s_max)
                
                # Show status
                st.caption(f"📊 Range: {s_min} to {s_max} | Y-Offset: {s_off:+.2f}µε | Showing {int(mask.sum())} points")
                
                # Create and display plot
                fig_strain = create_plotly_chart(
                    result['distance'][mask],
                    strain_data[mask],
                    f"Strain - {filename} (Offset: {s_off:+.2f}µε)",
                    "Strain (µε)",
                    '#3498db'
                )
                st.plotly_chart(fig_strain, use_container_width=True, key=f"splot_{file_id}_{reset_count}")
            
            else:  # BrillFrequency
                # ============================================
                # FREQUENCY PLOT
                # ============================================
                st.markdown(f"#### 📊 Frequency - {filename}")
                
                # Reset button
                if st.button(f"🔄 Reset Frequency", key=f"rst_freq_{file_id}", type="secondary"):
                    st.session_state[f'freq_reset_{file_id}'] += 1
                    st.rerun()
                
                # Controls
                with st.expander("⚙️ Frequency Controls", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    reset_count = st.session_state[f'freq_reset_{file_id}']
                    
                    with c1:
                        f_off = st.number_input(
                            "Y-Axis Offset (GHz)",
                            value=0.0,
                            step=0.01,
                            format="%.3f",
                            key=f"foff_{file_id}_{reset_count}",
                            help="Positive = Add, Negative = Subtract"
                        )
                    with c2:
                        f_min = st.number_input(
                            "X-Axis Min",
                            value=0,
                            min_value=0,
                            max_value=int(result['distance_points']-1),
                            key=f"fmin_{file_id}_{reset_count}"
                        )
                    with c3:
                        f_max = st.number_input(
                            "X-Axis Max",
                            value=int(result['distance_points']-1),
                            min_value=int(f_min + 1),
                            max_value=int(result['distance_points']-1),
                            key=f"fmax_{file_id}_{reset_count}"
                        )
                
                # Apply offset and filter
                freq_data = result['freq_first'] + f_off
                mask = (result['distance'] >= f_min) & (result['distance'] <= f_max)
                
                # Show status
                st.caption(f"📊 Range: {f_min} to {f_max} | Y-Offset: {f_off:+.3f}GHz | Showing {int(mask.sum())} points")
                
                # Create and display plot
                fig_freq = create_plotly_chart(
                    result['distance'][mask],
                    freq_data[mask],
                    f"Frequency - {filename} (Offset: {f_off:+.3f}GHz)",
                    "Frequency (GHz)",
                    '#9b59b6'
                )
                st.plotly_chart(fig_freq, use_container_width=True, key=f"fplot_{file_id}_{reset_count}")
                
                # ============================================
                # AMPLITUDE PLOT
                # ============================================
                st.markdown(f"#### 📈 Amplitude - {filename}")
                
                # Reset button
                if st.button(f"🔄 Reset Amplitude", key=f"rst_amp_{file_id}", type="secondary"):
                    st.session_state[f'amp_reset_{file_id}'] += 1
                    st.rerun()
                
                # Controls
                with st.expander("⚙️ Amplitude Controls", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    reset_count = st.session_state[f'amp_reset_{file_id}']
                    
                    with c1:
                        a_off = st.number_input(
                            "Y-Axis Offset",
                            value=0.0,
                            step=0.01,
                            format="%.3f",
                            key=f"aoff_{file_id}_{reset_count}",
                            help="Positive = Add, Negative = Subtract"
                        )
                    with c2:
                        a_min = st.number_input(
                            "X-Axis Min",
                            value=0,
                            min_value=0,
                            max_value=int(result['distance_points']-1),
                            key=f"amin_{file_id}_{reset_count}"
                        )
                    with c3:
                        a_max = st.number_input(
                            "X-Axis Max",
                            value=int(result['distance_points']-1),
                            min_value=int(a_min + 1),
                            max_value=int(result['distance_points']-1),
                            key=f"amax_{file_id}_{reset_count}"
                        )
                
                # Apply offset and filter
                amp_data = result['amp_first'] + a_off
                mask = (result['distance'] >= a_min) & (result['distance'] <= a_max)
                
                # Show status
                st.caption(f"📊 Range: {a_min} to {a_max} | Y-Offset: {a_off:+.3f} | Showing {int(mask.sum())} points")
                
                # Create and display plot
                fig_amp = create_plotly_chart(
                    result['distance'][mask],
                    amp_data[mask],
                    f"Amplitude - {filename} (Offset: {a_off:+.3f})",
                    "Amplitude (a.u.)",
                    '#16a085'
                )
                st.plotly_chart(fig_amp, use_container_width=True, key=f"aplot_{file_id}_{reset_count}")
    
    else:
        st.info("👆 Upload and process files to see analysis results")

# ============================================
# COMPARISON ANALYSIS (KEPT AS IS)
# ============================================

def show_comparison_analysis():
    """Compare two files side by side"""
    
    st.markdown("## ⚖️ Compare Two Files")
    st.info("Upload two files for comparative analysis")
    
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
                    st.success("✅ Files processed successfully!")
                else:
                    if not result1['success']:
                        st.error(f"❌ File 1 error: {result1['error']}")
                    if not result2['success']:
                        st.error(f"❌ File 2 error: {result2['error']}")
        
        # Display comparison results
        if 'compare_result1' in st.session_state and 'compare_result2' in st.session_state:
            result1 = st.session_state.compare_result1
            result2 = st.session_state.compare_result2
            fname1 = st.session_state.compare_file1_name
            fname2 = st.session_state.compare_file2_name
            
            st.divider()
            
            # Check if both are same type
            if result1['file_type'] != result2['file_type']:
                st.warning("⚠️ Files are different types! Comparison may not be meaningful.")
            
            # Comparison plots
            if result1['file_type'] == 'TempStrain' and result2['file_type'] == 'TempStrain':
                
                # Temperature comparison
                st.markdown("### 🌡️ Temperature Comparison")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=result1['distance'],
                    y=result1['temp_first'],
                    mode='lines',
                    name=fname1,
                    line=dict(color='#e74c3c', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=result2['distance'],
                    y=result2['temp_first'],
                    mode='lines',
                    name=fname2,
                    line=dict(color='#f39c12', width=2, dash='dash')
                ))
                fig.update_layout(
                    title="Temperature Comparison",
                    xaxis_title="Distance Index",
                    yaxis_title="Temperature (°C)",
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Strain comparison
                st.markdown("### 📏 Strain Comparison")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=result1['distance'],
                    y=result1['strain_first'],
                    mode='lines',
                    name=fname1,
                    line=dict(color='#3498db', width=2)
                ))
                fig.add_trace(go.Scatter(
                    x=result2['distance'],
                    y=result2['strain_first'],
                    mode='lines',
                    name=fname2,
                    line=dict(color='#9b59b6', width=2, dash='dash')
                ))
                fig.update_layout(
                    title="Strain Comparison",
                    xaxis_title="Distance Index",
                    yaxis_title="Strain (µε)",
                    template='plotly_white',
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Difference plot (if same dimensions)
                if result1['distance_points'] == result2['distance_points']:
                    st.markdown("### 📊 Difference Analysis")
                    
                    temp_diff = result2['temp_first'] - result1['temp_first']
                    strain_diff = result2['strain_first'] - result1['strain_first']
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### Temperature Difference")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=result1['distance'],
                            y=temp_diff,
                            mode='lines',
                            line=dict(color='#16a085', width=2),
                            fill='tozeroy'
                        ))
                        fig.update_layout(
                            title="Δ Temperature (File2 - File1)",
                            xaxis_title="Distance Index",
                            yaxis_title="ΔT (°C)",
                            template='plotly_white',
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### Strain Difference")
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=result1['distance'],
                            y=strain_diff,
                            mode='lines',
                            line=dict(color='#e67e22', width=2),
                            fill='tozeroy'
                        ))
                        fig.update_layout(
                            title="Δ Strain (File2 - File1)",
                            xaxis_title="Distance Index",
                            yaxis_title="Δε (µε)",
                            template='plotly_white',
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Files have different dimensions. Cannot calculate difference.")
            
            # Export comparison
            st.divider()
            if st.button("📥 Download Comparison PDF", use_container_width=True):
                with st.spinner("Generating comparison report..."):
                    try:
                        pdf_bytes = generate_pdf_report(
                            (result1, result2),
                            (fname1, fname2),
                            report_type='comparison'
                        )
                        st.download_button(
                            "⬇️ Download PDF",
                            pdf_bytes,
                            f"comparison_{fname1}_{fname2}.pdf",
                            "application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"PDF generation failed: {str(e)}")

# ============================================
# FILE HISTORY
# ============================================

def show_file_history():
    """Display processing history"""
    
    st.markdown("## 📜 Processing History")
    
    if 'processing_history' in st.session_state and st.session_state.processing_history:
        df = pd.DataFrame(st.session_state.processing_history)
        st.dataframe(df, use_container_width=True)
        
        if st.button("🗑️ Clear History"):
            st.session_state.processing_history = []
            st.rerun()
    else:
        st.info("No processing history yet. Process some files to see history here.")
