"""
PDF Report Generator
Generate professional PDF reports from analysis results
"""

import io
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
from datetime import datetime
import numpy as np

def generate_pdf_report(result_data, filename, report_type='single'):
    """
    Generate PDF report from analysis results
    
    Args:
        result_data: Analysis results (single dict or tuple of two dicts)
        filename: Original filename(s)
        report_type: 'single' or 'comparison'
        
    Returns:
        bytes: PDF file content
    """
    
    # Create PDF in memory
    buffer = io.BytesIO()
    pdf = pdf_backend.PdfPages(buffer)
    
    try:
        if report_type == 'single':
            _generate_single_report(pdf, result_data, filename)
        else:
            _generate_comparison_report(pdf, result_data, filename)
    finally:
        pdf.close()
    
    buffer.seek(0)
    return buffer.getvalue()

def _generate_single_report(pdf, result, filename):
    """Generate file analysis report"""
    
    # Detect file type
    file_type = result.get('file_type', 'TempStrain')
    
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
    
    # Metadata box - Handle both file types
    if file_type == 'TempStrain':
        data_shape = result['metadata']['strain_shape']
        temp_range = f"Temperature Range: {result['temp_first'].min():.2f} - {result['temp_first'].max():.2f} °C"
        strain_range = f"Strain Range: {result['strain_first'].min():.2f} - {result['strain_first'].max():.2f} µε"
        data_info = f"{temp_range}\n    {strain_range}"
    else:  # BrillFrequency
        data_shape = result['metadata']['freq_shape']
        freq_range = f"Frequency Range: {result['freq_first'].min():.2f} - {result['freq_first'].max():.2f} GHz"
        amp_range = f"Amplitude Range: {result['amp_first'].min():.2f} - {result['amp_first'].max():.2f} a.u."
        data_info = f"{freq_range}\n    {amp_range}"
    
    metadata_text = f"""
    Analysis Summary:
    ────────────────────────────────
    File Type: {file_type}
    Distance Points: {result['distance_points']}
    Time Samples: {len(result['time'])}
    Data Shape: {data_shape}
    
    {data_info}
    """
    
    fig.text(0.5, 0.25, metadata_text, 
             ha='center', va='center', fontsize=10, family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # Page 2 & 3: Plots based on file type
    if file_type == 'TempStrain':
        # Temperature plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(result['distance'], result['temp_first'], 'r-', linewidth=2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title('Temperature Distribution (First Sweep)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        stats_text = f"Min: {result['temp_first'].min():.2f}°C\nMax: {result['temp_first'].max():.2f}°C\nMean: {result['temp_first'].mean():.2f}°C\nStd: {result['temp_first'].std():.2f}°C"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Strain plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(result['distance'], result['strain_first'], 'b-', linewidth=2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Strain (µε)', fontsize=12)
        ax.set_title('Strain Distribution (First Sweep)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        stats_text = f"Min: {result['strain_first'].min():.2f} µε\nMax: {result['strain_first'].max():.2f} µε\nMean: {result['strain_first'].mean():.2f} µε\nStd: {result['strain_first'].std():.2f} µε"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
    
    else:  # BrillFrequency
        # Frequency plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(result['distance'], result['freq_first'], color='#9b59b6', linewidth=2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Frequency (GHz)', fontsize=12)
        ax.set_title('Brillouin Frequency Distribution (First Sweep)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        stats_text = f"Min: {result['freq_first'].min():.2f} GHz\nMax: {result['freq_first'].max():.2f} GHz\nMean: {result['freq_first'].mean():.2f} GHz\nStd: {result['freq_first'].std():.2f} GHz"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()
        
        # Amplitude plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(result['distance'], result['amp_first'], color='#16a085', linewidth=2)
        ax.set_xlabel('Distance Index', fontsize=12)
        ax.set_ylabel('Amplitude (a.u.)', fontsize=12)
        ax.set_title('Brillouin Amplitude Distribution (First Sweep)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        stats_text = f"Min: {result['amp_first'].min():.2f}\nMax: {result['amp_first'].max():.2f}\nMean: {result['amp_first'].mean():.2f}\nStd: {result['amp_first'].std():.2f}"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
        
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()

def _generate_comparison_report(pdf, results, filenames):
    """Generate comparison report for two files"""
    
    result1, result2 = results
    file1, file2 = filenames
    
    # Page 1: Cover page
    fig = plt.figure(figsize=(8.5, 11))
    fig.text(0.5, 0.7, 'DFOS Comparison Report', 
             ha='center', va='center', fontsize=32, fontweight='bold')
    fig.text(0.5, 0.6, 'Distributed Fiber Optic Sensing', 
             ha='center', va='center', fontsize=18, color='gray')
    fig.text(0.5, 0.5, f'File 1: {file1}', 
             ha='center', va='center', fontsize=12)
    fig.text(0.5, 0.47, f'File 2: {file2}', 
             ha='center', va='center', fontsize=12)
    fig.text(0.5, 0.42, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 
             ha='center', va='center', fontsize=11, color='gray')
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # Page 2: Temperature comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(result1['distance'], result1['temp_first'], 'r-', linewidth=2, label='File 1')
    ax.plot(result2['distance'], result2['temp_first'], 'orange', linestyle='--', linewidth=2, label='File 2')
    ax.set_xlabel('Distance Index', fontsize=12)
    ax.set_ylabel('Temperature (°C)', fontsize=12)
    ax.set_title('Temperature Comparison', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # Page 3: Strain comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(result1['distance'], result1['strain_first'], 'b-', linewidth=2, label='File 1')
    ax.plot(result2['distance'], result2['strain_first'], 'purple', linestyle='--', linewidth=2, label='File 2')
    ax.set_xlabel('Distance Index', fontsize=12)
    ax.set_ylabel('Strain (µε)', fontsize=12)
    ax.set_title('Strain Comparison', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # Page 4: Difference analysis (if dimensions match)
    if result1['distance_points'] == result2['distance_points']:
        temp_diff = result2['temp_first'] - result1['temp_first']
        strain_diff = result2['strain_first'] - result1['strain_first']
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
        
        # Temperature difference
        ax1.plot(result1['distance'], temp_diff, 'g-', linewidth=2)
        ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax1.set_xlabel('Distance Index', fontsize=12)
        ax1.set_ylabel('Temperature Difference (°C)', fontsize=12)
        ax1.set_title('Temperature Difference (File 2 - File 1)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        stats_text = f"Max: {np.max(np.abs(temp_diff)):.2f}°C\nMean: {np.mean(temp_diff):.2f}°C"
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
        
        # Strain difference
        ax2.plot(result1['distance'], strain_diff, 'm-', linewidth=2)
        ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax2.set_xlabel('Distance Index', fontsize=12)
        ax2.set_ylabel('Strain Difference (µε)', fontsize=12)
        ax2.set_title('Strain Difference (File 2 - File 1)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        stats_text = f"Max: {np.max(np.abs(strain_diff)):.2f} µε\nMean: {np.mean(strain_diff):.2f} µε"
        ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                fontsize=9)
        
        plt.tight_layout()
        pdf.savefig(fig, bbox_inches='tight')
        plt.close()