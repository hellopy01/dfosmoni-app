"""
PDF Report Generator - UPDATED
✅ Generates PDF with CURRENT state (offsets, ranges applied)
✅ Shows applied controls in PDF
✅ Support for Compare All view
"""

import io
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
from datetime import datetime
import numpy as np

def generate_pdf_report(result_data, filename, report_type='single', controls=None):
    """
    Generate PDF report with CURRENT STATE
    
    Args:
        result_data: Analysis results
        filename: Original filename(s)
        report_type: 'single', 'comparison', or 'compare_all'
        controls: Dict with offset/range values from current state
        
    Returns:
        bytes: PDF file content
    """
    
    buffer = io.BytesIO()
    pdf = pdf_backend.PdfPages(buffer)
    
    try:
        if report_type == 'single':
            _generate_single_report(pdf, result_data, filename, controls)
        elif report_type == 'compare_all':
            _generate_compare_all_report(pdf, result_data, filename, controls)
        else:
            _generate_comparison_report(pdf, result_data, filename)
    finally:
        pdf.close()
    
    buffer.seek(0)
    return buffer.getvalue()

def _generate_single_report(pdf, result, filename, controls=None):
    """Generate single file report with CURRENT state"""
    
    file_type = result.get('file_type', 'TempStrain')
    
    # Extract controls (offsets and ranges)
    if controls is None:
        controls = {}
    
    temp_offset = controls.get('temp_offset', 0.0)
    strain_offset = controls.get('strain_offset', 0.0)
    freq_offset = controls.get('freq_offset', 0.0)
    amp_offset = controls.get('amp_offset', 0.0)
    x_min = controls.get('x_min', 0)
    x_max = controls.get('x_max', result['distance_points'] - 1)
    
    # Page 1: Cover page
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.5, 0.7, 'DFOS Monitoring Report', 
             ha='center', va='center', fontsize=32, fontweight='bold')
    fig.text(0.5, 0.6, 'Distributed Fiber Optic Sensing', 
             ha='center', va='center', fontsize=18, color='gray')
    fig.text(0.5, 0.5, f'File: {filename}', 
             ha='center', va='center', fontsize=14)
    fig.text(0.5, 0.45, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
             ha='center', va='center', fontsize=12, color='gray')
    
    # Metadata with APPLIED CONTROLS
    if file_type == 'TempStrain':
        # Apply offsets to data
        temp_data = result['temp_first'] + temp_offset
        strain_data = result['strain_first'] + strain_offset
        
        data_shape = result['metadata']['strain_shape']
        temp_range = f"Temperature Range: {temp_data.min():.2f} - {temp_data.max():.2f} °C"
        strain_range = f"Strain Range: {strain_data.min():.2f} - {strain_data.max():.2f} µε"
        
        controls_info = f"""
    Applied Controls:
    ────────────────────────────────
    Temperature Y-Offset: {temp_offset:+.2f} °C
    Strain Y-Offset: {strain_offset:+.2f} µε
    X-Axis Range: {x_min} to {x_max}
    Distance Points: {result['distance_points']}
    Showing Points: {x_max - x_min + 1}
        """
        
        data_info = f"{temp_range}\n    {strain_range}"
    else:  # BrillFrequency
        # Apply offsets to data
        freq_data = result['freq_first'] + freq_offset
        amp_data = result['amp_first'] + amp_offset
        
        data_shape = result['metadata']['freq_shape']
        freq_range = f"Frequency Range: {freq_data.min():.3f} - {freq_data.max():.3f} GHz"
        amp_range = f"Amplitude Range: {amp_data.min():.3f} - {amp_data.max():.3f} a.u."
        
        controls_info = f"""
    Applied Controls:
    ────────────────────────────────
    Frequency Y-Offset: {freq_offset:+.3f} GHz
    Amplitude Y-Offset: {amp_offset:+.3f}
    X-Axis Range: {x_min} to {x_max}
    Distance Points: {result['distance_points']}
    Showing Points: {x_max - x_min + 1}
        """
        
        data_info = f"{freq_range}\n    {amp_range}"
    
    metadata_text = f"""
    Analysis Summary:
    ────────────────────────────────
    File Type: {file_type}
    Time Samples: {len(result['time'])}
    Data Shape: {data_shape}
    
    {data_info}
    {controls_info}
    """
    
    fig.text(0.5, 0.25, metadata_text, 
             ha='center', va='center', fontsize=9, family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # Apply range mask
    mask = (result['distance'] >= x_min) & (result['distance'] <= x_max)
    distance = result['distance'][mask]
    
    # Page 2 & 3: Plots with APPLIED controls
    if file_type == 'TempStrain':
        # Temperature plot
        fig, ax = plt.subplots(figsize=(10, 6))
        temp_plot_data = (result['temp_first'] + temp_offset)[mask]
        ax.plot(distance, temp_plot_data, 'r-', linewidth=2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title(f'Temperature Distribution (Offset: {temp_offset:+.2f}°C, Range: {x_min}-{x_max})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        stats_text = f"Min: {temp_plot_data.min():.2f}°C\nMax: {temp_plot_data.max():.2f}°C\nMean: {temp_plot_data.mean():.2f}°C\nStd: {temp_plot_data.std():.2f}°C"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=10)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Strain plot
        fig, ax = plt.subplots(figsize=(10, 6))
        strain_plot_data = (result['strain_first'] + strain_offset)[mask]
        ax.plot(distance, strain_plot_data, 'b-', linewidth=2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Strain (µε)', fontsize=12)
        ax.set_title(f'Strain Distribution (Offset: {strain_offset:+.2f}µε, Range: {x_min}-{x_max})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        stats_text = f"Min: {strain_plot_data.min():.2f}µε\nMax: {strain_plot_data.max():.2f}µε\nMean: {strain_plot_data.mean():.2f}µε\nStd: {strain_plot_data.std():.2f}µε"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=10)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    else:  # BrillFrequency
        # Frequency plot
        fig, ax = plt.subplots(figsize=(10, 6))
        freq_plot_data = (result['freq_first'] + freq_offset)[mask]
        ax.plot(distance, freq_plot_data, color='#9b59b6', linewidth=2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Frequency (GHz)', fontsize=12)
        ax.set_title(f'Frequency Distribution (Offset: {freq_offset:+.3f}GHz, Range: {x_min}-{x_max})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        stats_text = f"Min: {freq_plot_data.min():.3f}GHz\nMax: {freq_plot_data.max():.3f}GHz\nMean: {freq_plot_data.mean():.3f}GHz\nStd: {freq_plot_data.std():.3f}GHz"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=10)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Amplitude plot
        fig, ax = plt.subplots(figsize=(10, 6))
        amp_plot_data = (result['amp_first'] + amp_offset)[mask]
        ax.plot(distance, amp_plot_data, color='#16a085', linewidth=2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Amplitude (a.u.)', fontsize=12)
        ax.set_title(f'Amplitude Distribution (Offset: {amp_offset:+.3f}, Range: {x_min}-{x_max})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        stats_text = f"Min: {amp_plot_data.min():.3f}\nMax: {amp_plot_data.max():.3f}\nMean: {amp_plot_data.mean():.3f}\nStd: {amp_plot_data.std():.3f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=10)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

def _generate_compare_all_report(pdf, processed_files, filenames, controls):
    """Generate Compare All view PDF with all files combined"""
    
    # Color palette
    colors = [
        '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
        '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b'
    ]
    
    # Extract controls
    temp_offset = controls.get('temp_offset', 0.0)
    strain_offset = controls.get('strain_offset', 0.0)
    freq_offset = controls.get('freq_offset', 0.0)
    amp_offset = controls.get('amp_offset', 0.0)
    x_min = controls.get('x_min', 0)
    x_max = controls.get('x_max', 2500)
    
    # Separate by file type
    tempstrain_files = []
    brillfreq_files = []
    
    for fname, result in processed_files.items():
        if result['file_type'] == 'TempStrain':
            tempstrain_files.append((fname, result))
        else:
            brillfreq_files.append((fname, result))
    
    # Page 1: Cover
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.5, 0.7, 'DFOS Compare All Report', 
             ha='center', va='center', fontsize=32, fontweight='bold')
    fig.text(0.5, 0.6, 'Multiple Files Combined Analysis', 
             ha='center', va='center', fontsize=18, color='gray')
    fig.text(0.5, 0.5, f'Total Files: {len(processed_files)}', 
             ha='center', va='center', fontsize=14)
    fig.text(0.5, 0.45, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
             ha='center', va='center', fontsize=12, color='gray')
    
    # File list
    files_list = "\n".join([f"• {fname}" for fname in processed_files.keys()])
    fig.text(0.5, 0.3, f"Files Analyzed:\n{files_list}", 
             ha='center', va='center', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # TempStrain combined plots
    if tempstrain_files:
        # Combined Temperature
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for idx, (fname, result) in enumerate(tempstrain_files):
            color = colors[idx % len(colors)]
            temp_data = result['temp_first'] + temp_offset
            mask = (result['distance'] >= x_min) & (result['distance'] <= x_max)
            ax.plot(result['distance'][mask], temp_data[mask], 
                   color=color, linewidth=2, label=fname, alpha=0.8)
        
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title(f'Combined Temperature (Offset: {temp_offset:+.2f}°C, Range: {x_min}-{x_max})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Combined Strain
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for idx, (fname, result) in enumerate(tempstrain_files):
            color = colors[idx % len(colors)]
            strain_data = result['strain_first'] + strain_offset
            mask = (result['distance'] >= x_min) & (result['distance'] <= x_max)
            ax.plot(result['distance'][mask], strain_data[mask], 
                   color=color, linewidth=2, label=fname, alpha=0.8)
        
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Strain (µε)', fontsize=12)
        ax.set_title(f'Combined Strain (Offset: {strain_offset:+.2f}µε, Range: {x_min}-{x_max})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    # BrillFreq combined plots
    if brillfreq_files:
        # Combined Frequency
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for idx, (fname, result) in enumerate(brillfreq_files):
            color = colors[idx % len(colors)]
            freq_data = result['freq_first'] + freq_offset
            mask = (result['distance'] >= x_min) & (result['distance'] <= x_max)
            ax.plot(result['distance'][mask], freq_data[mask], 
                   color=color, linewidth=2, label=fname, alpha=0.8)
        
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Frequency (GHz)', fontsize=12)
        ax.set_title(f'Combined Frequency (Offset: {freq_offset:+.3f}GHz, Range: {x_min}-{x_max})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Combined Amplitude
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for idx, (fname, result) in enumerate(brillfreq_files):
            color = colors[idx % len(colors)]
            amp_data = result['amp_first'] + amp_offset
            mask = (result['distance'] >= x_min) & (result['distance'] <= x_max)
            ax.plot(result['distance'][mask], amp_data[mask], 
                   color=color, linewidth=2, label=fname, alpha=0.8)
        
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Amplitude (a.u.)', fontsize=12)
        ax.set_title(f'Combined Amplitude (Offset: {amp_offset:+.3f}, Range: {x_min}-{x_max})', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

def _generate_comparison_report(pdf, result_data, filenames):
    """Generate comparison report (2 files)"""
    
    result1, result2 = result_data
    fname1, fname2 = filenames
    
    # Cover page
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.5, 0.7, 'DFOS Comparison Report', 
             ha='center', va='center', fontsize=32, fontweight='bold')
    fig.text(0.5, 0.6, 'Two File Comparison Analysis', 
             ha='center', va='center', fontsize=18, color='gray')
    fig.text(0.5, 0.5, f'File 1: {fname1}', 
             ha='center', va='center', fontsize=12)
    fig.text(0.5, 0.45, f'File 2: {fname2}', 
             ha='center', va='center', fontsize=12)
    fig.text(0.5, 0.4, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
             ha='center', va='center', fontsize=10, color='gray')
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # Temperature comparison
    if result1['file_type'] == 'TempStrain':
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(result1['distance'], result1['temp_first'], 'r-', linewidth=2, label=fname1)
        ax.plot(result2['distance'], result2['temp_first'], 'b--', linewidth=2, label=fname2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title('Temperature Comparison', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Strain comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(result1['distance'], result1['strain_first'], 'r-', linewidth=2, label=fname1)
        ax.plot(result2['distance'], result2['strain_first'], 'b--', linewidth=2, label=fname2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Strain (µε)', fontsize=12)
        ax.set_title('Strain Comparison', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
