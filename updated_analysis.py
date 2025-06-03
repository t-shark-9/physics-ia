#!/usr/bin/env python3
"""
Updated data analysis script for physics IA - reorganized with all measurements
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd

# Set up plotting style
plt.style.use('default')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

def parse_all_measurements():
    """Parse all individual measurements from the data file"""
    
    # Individual measurements data (extracted from file, organized by pump amount)
    # Format: [pump_amount, repetition, peak_start, peak_end, peak_height]
    measurements = [
        # 10 pumps
        [10, 1, 3.8678, 3.8821, 14],
        [10, 2, 2.3507, 2.3630, 17], 
        [10, 3, 1.5973, 1.6063, 16],
        [10, 4, 2.1055, 2.1473, 4],
        [10, 5, 2.2739, 2.2986, 5],
        
        # 20 pumps  
        [20, 1, 2.1416, 2.1864, 12],
        [20, 2, 2.1203, 2.1328, 17],
        [20, 3, 1.9926, 2.0040, 20],
        [20, 4, 3.6033, 3.6281, 17],
        [20, 5, 2.0122, 2.0399, 14],
        
        # 30 pumps
        [30, 1, 2.9819, 3.0025, 24],
        [30, 2, 1.8302, 1.8451, 27],
        [30, 3, 2.6686, 2.6769, 24],
        [30, 4, 4.0077, 4.0328, 20],
        [30, 5, 4.6452, 4.6890, 11],
        
        # 40 pumps
        [40, 1, 4.8642, 4.9227, 12],
        [40, 2, 3.5060, 3.5140, 40],
        [40, 3, 2.0100, 2.0240, 26],
        [40, 4, 1.7300, 1.7791, 12],
        [40, 5, 2.6613, 2.6804, 19],
        
        # 50 pumps
        [50, 1, 2.5071, 2.5843, 19],
        [50, 2, 2.3462, 2.3567, 34],
        [50, 3, 2.1928, 2.2020, 32],
        [50, 4, 3.0298, 3.0876, 22],
        [50, 5, 2.6245, 2.6689, 30]
    ]
    
    # Calculate impulse for each measurement
    for measurement in measurements:
        change_in_time = measurement[3] - measurement[2]  # peak_end - peak_start
        peak_height = measurement[4]
        impulse = change_in_time * peak_height
        measurement.append(change_in_time)
        measurement.append(impulse)
    
    return measurements

def get_pressure_data():
    """Get pressure data ordered from 10 to 50 pumps"""
    # Pressure data with absolute uncertainties
    pressure_data = [
        [10, 0.000630, 2.560E+05, 3.29, 8422],
        [20, 0.001010, 4.105E+05, 3.16, 12972],
        [30, 0.001390, 5.649E+05, 3.12, 17625],
        [40, 0.001770, 7.193E+05, 3.10, 22298],
        [50, 0.002150, 8.738E+05, 3.08, 26913]
    ]
    return pressure_data

def get_impulse_summary():
    """Get impulse summary data ordered from 10 to 50 pumps"""
    impulse_summary = [
        [10, 0.0204, 11, 0.11, 9.91, 0.02],
        [20, 0.0242, 16, 0.19, 7.08, 0.08], 
        [30, 0.0225, 21, 0.24, 5.60, 0.07],
        [40, 0.0297, 22, 0.32, 5.26, 0.10],
        [50, 0.0398, 27, 0.55, 4.15, 0.29]
    ]
    return impulse_summary

def create_comprehensive_table():
    """Create comprehensive table with all measurements"""
    measurements = parse_all_measurements()
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis('off')
    
    # Prepare table data
    headers = ['Pumps', 'Rep', 'Peak Start (s)', 'Peak End (s)', 'Peak Height (N)', 'Change in Time (s)', 'Impulse (Ns)']
    
    table_data = []
    for measurement in measurements:
        pumps, rep, start, end, height, change_time, impulse = measurement
        table_data.append([
            f'{pumps}', f'{rep}', f'{start:.4f}', f'{end:.4f}', 
            f'{height}', f'{change_time:.4f}', f'{impulse:.4f}'
        ])
    
    # Create table
    table = ax.table(cellText=table_data, colLabels=headers, 
                    cellLoc='center', loc='center',
                    colWidths=[0.1, 0.1, 0.15, 0.15, 0.15, 0.15, 0.15])
    
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    
    # Style the table
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#E6E6FA')
        table[(0, i)].set_text_props(weight='bold')
    
    # Color rows by pump amount
    colors = ['#F0F8FF', '#F8F8FF', '#F0FFF0', '#FFF8DC', '#FFE4E1']
    pump_amounts = [10, 20, 30, 40, 50]
    
    for i, row in enumerate(table_data):
        pump_amount = int(row[0])
        color_index = pump_amounts.index(pump_amount)
        for j in range(len(headers)):
            table[(i+1, j)].set_facecolor(colors[color_index])
    
    plt.title('Complete Measurements: All Pump Amounts and Repetitions', 
              fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/workspaces/physics-ia/complete_measurements_table.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_pressure_table():
    """Create updated pressure table with absolute uncertainties included"""
    pressure_data = get_pressure_data()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')
    
    # Table data with absolute uncertainty included in pressure values
    headers = ['Pumps', 'Volume (m³)', 'Pressure (Pa)', 'Relative Uncertainty (%)']
    data = []
    
    for row in pressure_data:
        pumps, volume, pressure, rel_unc, abs_unc = row
        pressure_with_unc = f'({pressure/1e5:.2f} ± {abs_unc/1e5:.2f}) × 10⁵'
        data.append([
            str(pumps),
            f'{volume:.6f} ± 0.000002',
            pressure_with_unc,
            f'{rel_unc:.2f}'
        ])
    
    # Create table
    table = ax.table(cellText=data, colLabels=headers, 
                    cellLoc='center', loc='center',
                    colWidths=[0.2, 0.3, 0.3, 0.2])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style the table
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#E6E6FA')
        table[(0, i)].set_text_props(weight='bold')
    
    for i in range(1, len(data) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F8F8FF')
    
    plt.title('Pressure Measurements (10-50 pumps)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/workspaces/physics-ia/pressure_table_updated.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_impulse_table():
    """Create updated impulse table ordered from 10 to 50 pumps"""
    impulse_data = get_impulse_summary()
    
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis('off')
    
    # Table data
    headers = ['Pumps', 'Change in Time (s)', 'Peak Height (N)', 'Impulse (Ns)', 'Uncertainty (%)', 'Range (Ns)']
    data = []
    
    for row in impulse_data:
        pumps, change_time, peak_height, impulse, uncertainty, range_val = row
        data.append([
            str(pumps), f'{change_time:.4f}', str(peak_height), 
            f'{impulse:.2f}', f'{uncertainty:.2f}', f'{range_val:.2f}'
        ])
    
    # Create table
    table = ax.table(cellText=data, colLabels=headers, 
                    cellLoc='center', loc='center',
                    colWidths=[0.12, 0.18, 0.18, 0.18, 0.18, 0.16])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    # Style the table
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#E6E6FA')
        table[(0, i)].set_text_props(weight='bold')
    
    for i in range(1, len(data) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#F8F8FF')
    
    plt.title('Impulse Measurements Summary (10-50 pumps)', 
              fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('/workspaces/physics-ia/impulse_table_updated.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_updated_graph():
    """Create updated graph with data ordered from 10 to 50 pumps"""
    pressure_data = get_pressure_data()
    impulse_data = get_impulse_summary()
    
    # Extract data for plotting
    pressures = [row[2] for row in pressure_data]  # Pressure in Pa
    impulses = [row[3] for row in impulse_data]    # Impulse in Ns
    pressure_errors = [row[4] for row in pressure_data]  # Absolute uncertainty in Pa
    impulse_errors = [row[5] for row in impulse_data]    # Range in Ns
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Plot data points with error bars
    ax.errorbar(pressures, impulses, xerr=pressure_errors, yerr=impulse_errors,
                fmt='bo', markersize=8, capsize=5, capthick=2, elinewidth=2,
                label='Experimental data', alpha=0.8)
    
    # Calculate best fit line
    slope, intercept, r_value, p_value, std_err = stats.linregress(pressures, impulses)
    
    # Calculate line through origin
    slope_origin = np.sum(np.array(pressures) * np.array(impulses)) / np.sum(np.array(pressures)**2)
    
    # Create extended range for trend lines (including origin)
    x_min = 0
    x_max = max(pressures) * 1.1
    x_trend = np.linspace(x_min, x_max, 100)
    
    # Plot trend lines
    y_trend_fit = slope * x_trend + intercept
    y_trend_origin = slope_origin * x_trend
    
    ax.plot(x_trend, y_trend_fit, 'r-', linewidth=2, 
            label=f'Best fit: y = {slope:.2e}x + {intercept:.3f}\n(R² = {r_value**2:.4f})')
    ax.plot(x_trend, y_trend_origin, 'g--', linewidth=2,
            label=f'Through origin: y = {slope_origin:.2e}x\n(R² = {1 - np.sum((np.array(impulses) - slope_origin * np.array(pressures))**2) / np.sum((np.array(impulses) - np.mean(impulses))**2):.4f})')
    
    # Formatting
    ax.set_xlabel('Pressure (Pa)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Impulse (Ns)', fontsize=12, fontweight='bold')
    ax.set_title('Pressure vs Impulse Relationship\n(Data ordered from 10-50 pumps)', 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    # Set axis limits to show origin
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, max(impulses) * 1.1)
    
    plt.tight_layout()
    plt.savefig('/workspaces/physics-ia/pressure_vs_impulse_updated.png', dpi=300, bbox_inches='tight')
    plt.savefig('/workspaces/physics-ia/pressure_vs_impulse_updated.pdf', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    print("Creating updated tables and graphs...")
    
    create_comprehensive_table()
    print("✓ Created complete_measurements_table.png")
    
    create_pressure_table()
    print("✓ Created pressure_table_updated.png")
    
    create_impulse_table()
    print("✓ Created impulse_table_updated.png")
    
    create_updated_graph()
    print("✓ Created pressure_vs_impulse_updated.png and .pdf")
    
    print("\nAll updated files created successfully!")
    print("Data now ordered from 10-50 pumps with absolute uncertainties included.")
