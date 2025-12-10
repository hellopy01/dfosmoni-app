"""
File Analysis Components - COMPLETE WITH COMPARE ALL FEATURE
✅ Multiple file upload
✅ Individual controls per file
✅ NEW: Compare All Charts - Plot all files in single graph
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
    """
    try:
        with h5py.File(file_obj, "r") as f:
            base_path = "Acquisition/Custom/Brillouin[0]/"
            time = f[base_path + "BrillouinDataTime"][:]
            
            has_strain = (base_path + "StrainData") in f
            has_temp = (base_path + "TemperatureData") in f
            has_freq = (base_path + "FrequencyData") in f
            has_amp = (base_path + "AmplitudeData") in f
            
            if has_strain and has_temp:
                strain = f[base_path + "StrainData"][:]
                temp = f[base_path + "TemperatureData"][:]
                distance_points = strain.shape[1]
                distance = np.arange(distance_points)
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
            
            elif has_freq and has_amp:
                freq = f[base_path + "FrequencyData"][:]
                amp = f[base_path + "AmplitudeData"][:]
                distance_points = freq.shape[1]
                distance = np.arange(distance_points)
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
                    'error': 'Unknown file format'
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
# PLOTTING
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
# COMPARE ALL CHARTS FUNCTION
# ============================================

def show_compare_all_charts(processed_files):
    """Show all files plotted together in single charts with different colors"""
    
    st.markdown("## 📊 Compare All Files - Combined View")
    st.info("All processed files plotted together with different colors")
    
    # Color palette for multiple files
    colors = [
        '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
        '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b',
        '#8e44ad', '#27ae60', '#d35400', '#2980b9', '#f1c40f'
    ]
    
    # Separate files by type
    tempstrain_files = []
    brillfreq_files = []
    
    for fname, result in processed_files.items():
        if result['file_type'] == 'TempStrain':
            tempstrain_files.append((fname, result))
        else:
            brillfreq_files.append((fname, result))
    
    # ============================================
    # TEMPSTRAIN FILES - COMBINED CHARTS
    # ============================================
    if tempstrain_files:
        st.markdown("### 🌡️ TempStrain Files Combined")
        
        # Initialize controls state
        if 'compare_temp_offset' not in st.session_state:
            st.session_state.compare_temp_offset = 0.0
        if 'compare_strain_offset' not in st.session_state:
            st.session_state.compare_strain_offset = 0.0
        if 'compare_x_min' not in st.session_state:
            st.session_state.compare_x_min = 0
        if 'compare_x_max' not in st.session_state:
            max_points = max([r['distance_points'] for _, r in tempstrain_files])
            st.session_state.compare_x_max = max_points - 1
        
        # COMBINED TEMPERATURE CHART
        st.markdown("#### 🌡️ All Temperature Data")
        
        with st.expander("⚙️ Temperature Controls (Applied to All)", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                temp_offset = st.number_input(
                    "Y-Axis Offset (°C)",
                    value=st.session_state.compare_temp_offset,
                    step=0.1,
                    format="%.2f",
                    key="cmp_temp_offset",
                    help="Applied to all files"
                )
                st.session_state.compare_temp_offset = temp_offset
            
            with col2:
                max_points_temp = max([r['distance_points'] for _, r in tempstrain_files])
                x_min = st.number_input(
                    "X-Axis Min",
                    value=st.session_state.compare_x_min,
                    min_value=0,
                    max_value=max_points_temp-1,
                    key="cmp_x_min"
                )
                st.session_state.compare_x_min = x_min
            
            with col3:
                x_max = st.number_input(
                    "X-Axis Max",
                    value=st.session_state.compare_x_max,
                    min_value=x_min+1,
                    max_value=max_points_temp-1,
                    key="cmp_x_max"
                )
                st.session_state.compare_x_max = x_max
        
        # Create combined temperature plot
        fig_temp = go.Figure()
        for idx, (fname, result) in enumerate(tempstrain_files):
            color = colors[idx % len(colors)]
            temp_data = result['temp_first'] + temp_offset
            mask = (result['distance'] >= x_min) & (result['distance'] <= x_max)
            
            fig_temp.add_trace(go.Scatter(
                x=result['distance'][mask],
                y=temp_data[mask],
                mode='lines',
                name=fname,
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{fname}</b><br>Distance: %{{x}}<br>Temp: %{{y:.2f}}°C<extra></extra>'
            ))
        
        fig_temp.update_layout(
            title=f"Combined Temperature (Offset: {temp_offset:+.2f}°C)",
            xaxis_title="Distance Index",
            yaxis_title="Temperature (°C)",
            template='plotly_white',
            hovermode='x unified',
            height=600,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        fig_temp.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig_temp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        st.plotly_chart(fig_temp, use_container_width=True)
        
        # COMBINED STRAIN CHART
        st.markdown("#### 📏 All Strain Data")
        
        with st.expander("⚙️ Strain Controls (Applied to All)", expanded=False):
            strain_offset = st.number_input(
                "Y-Axis Offset (µε)",
                value=st.session_state.compare_strain_offset,
                step=1.0,
                format="%.2f",
                key="cmp_strain_offset",
                help="Applied to all files"
            )
            st.session_state.compare_strain_offset = strain_offset
        
        # Create combined strain plot
        fig_strain = go.Figure()
        for idx, (fname, result) in enumerate(tempstrain_files):
            color = colors[idx % len(colors)]
            strain_data = result['strain_first'] + strain_offset
            mask = (result['distance'] >= x_min) & (result['distance'] <= x_max)
            
            fig_strain.add_trace(go.Scatter(
                x=result['distance'][mask],
                y=strain_data[mask],
                mode='lines',
                name=fname,
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{fname}</b><br>Distance: %{{x}}<br>Strain: %{{y:.2f}}µε<extra></extra>'
            ))
        
        fig_strain.update_layout(
            title=f"Combined Strain (Offset: {strain_offset:+.2f}µε)",
            xaxis_title="Distance Index",
            yaxis_title="Strain (µε)",
            template='plotly_white',
            hovermode='x unified',
            height=600,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        fig_strain.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig_strain.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        st.plotly_chart(fig_strain, use_container_width=True)
    
    # ============================================
    # BRILLFREQ FILES - COMBINED CHARTS
    # ============================================
    if brillfreq_files:
        st.markdown("### 📡 BrillFrequency Files Combined")
        
        # Initialize controls
        if 'compare_freq_offset' not in st.session_state:
            st.session_state.compare_freq_offset = 0.0
        if 'compare_amp_offset' not in st.session_state:
            st.session_state.compare_amp_offset = 0.0
        if 'compare_freq_x_min' not in st.session_state:
            st.session_state.compare_freq_x_min = 0
        if 'compare_freq_x_max' not in st.session_state:
            max_points = max([r['distance_points'] for _, r in brillfreq_files])
            st.session_state.compare_freq_x_max = max_points - 1
        
        # COMBINED FREQUENCY CHART
        st.markdown("#### 📊 All Frequency Data")
        
        with st.expander("⚙️ Frequency Controls (Applied to All)", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                freq_offset = st.number_input(
                    "Y-Axis Offset (GHz)",
                    value=st.session_state.compare_freq_offset,
                    step=0.01,
                    format="%.3f",
                    key="cmp_freq_offset"
                )
                st.session_state.compare_freq_offset = freq_offset
            
            with col2:
                max_points_freq = max([r['distance_points'] for _, r in brillfreq_files])
                freq_x_min = st.number_input(
                    "X-Axis Min",
                    value=st.session_state.compare_freq_x_min,
                    min_value=0,
                    max_value=max_points_freq-1,
                    key="cmp_freq_x_min"
                )
                st.session_state.compare_freq_x_min = freq_x_min
            
            with col3:
                freq_x_max = st.number_input(
                    "X-Axis Max",
                    value=st.session_state.compare_freq_x_max,
                    min_value=freq_x_min+1,
                    max_value=max_points_freq-1,
                    key="cmp_freq_x_max"
                )
                st.session_state.compare_freq_x_max = freq_x_max
        
        # Create combined frequency plot
        fig_freq = go.Figure()
        for idx, (fname, result) in enumerate(brillfreq_files):
            color = colors[idx % len(colors)]
            freq_data = result['freq_first'] + freq_offset
            mask = (result['distance'] >= freq_x_min) & (result['distance'] <= freq_x_max)
            
            fig_freq.add_trace(go.Scatter(
                x=result['distance'][mask],
                y=freq_data[mask],
                mode='lines',
                name=fname,
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{fname}</b><br>Distance: %{{x}}<br>Freq: %{{y:.3f}}GHz<extra></extra>'
            ))
        
        fig_freq.update_layout(
            title=f"Combined Frequency (Offset: {freq_offset:+.3f}GHz)",
            xaxis_title="Distance Index",
            yaxis_title="Frequency (GHz)",
            template='plotly_white',
            hovermode='x unified',
            height=600,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        fig_freq.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig_freq.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        st.plotly_chart(fig_freq, use_container_width=True)
        
        # COMBINED AMPLITUDE CHART
        st.markdown("#### 📈 All Amplitude Data")
        
        with st.expander("⚙️ Amplitude Controls (Applied to All)", expanded=False):
            amp_offset = st.number_input(
                "Y-Axis Offset",
                value=st.session_state.compare_amp_offset,
                step=0.01,
                format="%.3f",
                key="cmp_amp_offset"
            )
            st.session_state.compare_amp_offset = amp_offset
        
        # Create combined amplitude plot
        fig_amp = go.Figure()
        for idx, (fname, result) in enumerate(brillfreq_files):
            color = colors[idx % len(colors)]
            amp_data = result['amp_first'] + amp_offset
            mask = (result['distance'] >= freq_x_min) & (result['distance'] <= freq_x_max)
            
            fig_amp.add_trace(go.Scatter(
                x=result['distance'][mask],
                y=amp_data[mask],
                mode='lines',
                name=fname,
                line=dict(color=color, width=2),
                hovertemplate=f'<b>{fname}</b><br>Distance: %{{x}}<br>Amp: %{{y:.3f}}<extra></extra>'
            ))
        
        fig_amp.update_layout(
            title=f"Combined Amplitude (Offset: {amp_offset:+.3f})",
            xaxis_title="Distance Index",
            yaxis_title="Amplitude (a.u.)",
            template='plotly_white',
            hovermode='x unified',
            height=600,
            legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        fig_amp.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        fig_amp.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
        
        st.plotly_chart(fig_amp, use_container_width=True)
    
    # Back button
    st.divider()
    if st.button("⬅️ Back to Individual Analysis", type="secondary", use_container_width=True):
        st.session_state.show_compare_all = False
        st.rerun()

# ============================================
# MULTIPLE FILE ANALYSIS
# ============================================

def show_single_file_analysis():
    """Multiple File Analysis with Compare All feature"""
    
    # Check if we should show compare all view
    if 'show_compare_all' not in st.session_state:
        st.session_state.show_compare_all = False
    
    if st.session_state.show_compare_all and st.session_state.processed_files:
        show_compare_all_charts(st.session_state.processed_files)
        return
    
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
                    if uploaded and uploaded.name in st.session_state.processed_files:
                        del st.session_state.processed_files[uploaded.name]
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
        
        # Header with Compare All button
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.markdown("## 📊 Analysis Results")
        with col2:
            # COMPARE ALL BUTTON - NEW FEATURE
            if len(st.session_state.processed_files) >= 2:
                if st.button("📊 Compare All Charts", type="primary", use_container_width=True):
                    st.session_state.show_compare_all = True
                    st.rerun()
        with col3:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                st.session_state.processed_files = {}
                st.rerun()
        
        # Show each file's results (REST OF CODE UNCHANGED)
        for filename, result in list(st.session_state.processed_files.items()):
            st.markdown("---")
            
            cols = st.columns([5, 1])
            with cols[0]:
                emoji = "🌡️" if result['file_type'] == 'TempStrain' else "📡"
                st.markdown(f"### {emoji} **{filename}**")
                st.caption(f"📊 Type: **{result['file_type']}** | Points: **{result['distance_points']}** | Samples: **{len(result['time'])}**")
            with cols[1]:
                if st.button("❌ Remove", key=f"del_{filename}", help="Remove", use_container_width=True):
                    del st.session_state.processed_files[filename]
                    st.rerun()
            
            file_id = filename.replace('.', '_').replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
            
            for plot_type in ['temp', 'strain', 'freq', 'amp']:
                key = f'{plot_type}_reset_{file_id}'
                if key not in st.session_state:
                    st.session_state[key] = 0
            
            with st.expander("📥 Export Options", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
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
                                st.error(f"PDF error: {str(e)}")
            
            # Display plots (SAME AS BEFORE - NO CHANGES)
            if result['file_type'] == 'TempStrain':
                # TEMPERATURE
                st.markdown(f"#### 🌡️ Temperature - {filename}")
                
                if st.button(f"🔄 Reset Temperature", key=f"rst_temp_{file_id}", type="secondary"):
                    st.session_state[f'temp_reset_{file_id}'] += 1
                    st.rerun()
                
                with st.expander("⚙️ Temperature Controls", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    reset_count = st.session_state[f'temp_reset_{file_id}']
                    
                    with c1:
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
                
                temp_data = result['temp_first'] + t_off
                mask = (result['distance'] >= t_min) & (result['distance'] <= t_max)
                st.caption(f"📊 Range: {t_min}-{t_max} | Offset: {t_off:+.2f}°C | Points: {int(mask.sum())}")
                
                fig_temp = create_plotly_chart(
                    result['distance'][mask],
                    temp_data[mask],
                    f"Temperature - {filename} (Offset: {t_off:+.2f}°C)",
                    "Temperature (°C)",
                    '#e74c3c'
                )
                st.plotly_chart(fig_temp, use_container_width=True, key=f"plot_temp_{file_id}_{reset_count}")
                
                # STRAIN
                st.markdown(f"#### 📏 Strain - {filename}")
                
                if st.button(f"🔄 Reset Strain", key=f"rst_strain_{file_id}", type="secondary"):
                    st.session_state[f'strain_reset_{file_id}'] += 1
                    st.rerun()
                
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
                
                strain_data = result['strain_first'] + s_off
                mask = (result['distance'] >= s_min) & (result['distance'] <= s_max)
                st.caption(f"📊 Range: {s_min}-{s_max} | Offset: {s_off:+.2f}µε | Points: {int(mask.sum())}")
                
                fig_strain = create_plotly_chart(
                    result['distance'][mask],
                    strain_data[mask],
                    f"Strain - {filename} (Offset: {s_off:+.2f}µε)",
                    "Strain (µε)",
                    '#3498db'
                )
                st.plotly_chart(fig_strain, use_container_width=True, key=f"plot_strain_{file_id}_{reset_count}")
            
            else:  # BrillFrequency (SAME AS BEFORE)
                # FREQUENCY
                st.markdown(f"#### 📊 Frequency - {filename}")
                
                if st.button(f"🔄 Reset Frequency", key=f"rst_freq_{file_id}", type="secondary"):
                    st.session_state[f'freq_reset_{file_id}'] += 1
                    st.rerun()
                
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
                
                freq_data = result['freq_first'] + f_off
                mask = (result['distance'] >= f_min) & (result['distance'] <= f_max)
                st.caption(f"📊 Range: {f_min}-{f_max} | Offset: {f_off:+.3f}GHz | Points: {int(mask.sum())}")
                
                fig_freq = create_plotly_chart(
                    result['distance'][mask],
                    freq_data[mask],
                    f"Frequency - {filename} (Offset: {f_off:+.3f}GHz)",
                    "Frequency (GHz)",
                    '#9b59b6'
                )
                st.plotly_chart(fig_freq, use_container_width=True, key=f"plot_freq_{file_id}_{reset_count}")
                
                # AMPLITUDE
                st.markdown(f"#### 📈 Amplitude - {filename}")
                
                if st.button(f"🔄 Reset Amplitude", key=f"rst_amp_{file_id}", type="secondary"):
                    st.session_state[f'amp_reset_{file_id}'] += 1
                    st.rerun()
                
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
                
                amp_data = result['amp_first'] + a_off
                mask = (result['distance'] >= a_min) & (result['distance'] <= a_max)
                st.caption(f"📊 Range: {a_min}-{a_max} | Offset: {a_off:+.3f} | Points: {int(mask.sum())}")
                
                fig_amp = create_plotly_chart(
                    result['distance'][mask],
                    amp_data[mask],
                    f"Amplitude - {filename} (Offset: {a_off:+.3f})",
                    "Amplitude (a.u.)",
                    '#16a085'
                )
                st.plotly_chart(fig_amp, use_container_width=True, key=f"plot_amp_{file_id}_{reset_count}")
    
    else:
        st.info("👆 Upload and process files to see analysis results")

# ============================================
# COMPARISON & HISTORY (UNCHANGED)
# ============================================

def show_comparison_analysis():
    """Compare two files side by side"""
    st.markdown("## ⚖️ Compare Two Files")
    st.info("Upload two files for comparative analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📁 File 1")
        file1 = st.file_uploader("Choose first file", type=['h5', 'bts'], key='cmp1')
        if file1:
            st.success(f"✅ {file1.name}")
    
    with col2:
        st.markdown("#### 📁 File 2")
        file2 = st.file_uploader("Choose second file", type=['h5', 'bts'], key='cmp2')
        if file2:
            st.success(f"✅ {file2.name}")
    
    if file1 and file2:
        if st.button("🔬 Compare", type="primary", use_container_width=True):
            with st.spinner("Processing..."):
                r1 = process_bts_file(file1)
                r2 = process_bts_file(file2)
                
                if r1['success'] and r2['success']:
                    st.session_state.cmp_r1 = r1
                    st.session_state.cmp_r2 = r2
                    st.session_state.cmp_f1 = file1.name
                    st.session_state.cmp_f2 = file2.name
                    st.success("✅ Processed!")
                else:
                    st.error("❌ Processing failed")
        
        if 'cmp_r1' in st.session_state:
            r1 = st.session_state.cmp_r1
            r2 = st.session_state.cmp_r2
            
            st.divider()
            
            if r1['file_type'] == 'TempStrain' and r2['file_type'] == 'TempStrain':
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=r1['distance'], y=r1['temp_first'], name="File 1", line=dict(color='#e74c3c')))
                fig.add_trace(go.Scatter(x=r2['distance'], y=r2['temp_first'], name="File 2", line=dict(color='#f39c12', dash='dash')))
                fig.update_layout(title="Temperature Comparison", xaxis_title="Distance", yaxis_title="Temperature (°C)", height=500)
                st.plotly_chart(fig, use_container_width=True)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=r1['distance'], y=r1['strain_first'], name="File 1", line=dict(color='#3498db')))
                fig.add_trace(go.Scatter(x=r2['distance'], y=r2['strain_first'], name="File 2", line=dict(color='#9b59b6', dash='dash')))
                fig.update_layout(title="Strain Comparison", xaxis_title="Distance", yaxis_title="Strain (µε)", height=500)
                st.plotly_chart(fig, use_container_width=True)

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
        st.info("No history yet")
