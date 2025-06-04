#!/usr/bin/env python3
"""
Final data analysis script for physics IA - updated graph with blue line of best fit
and minimum/maximum lines through error bars, fixed at atmospheric pressure
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Set up plotting style
plt.style.use('default')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.size'] = 10

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

def create_updated_graph():
    """Create updated graph with blue line of best fit and min/max lines through error bars"""
    pressure_data = get_pressure_data()
    impulse_data = get_impulse_summary()
    
    # Extract data for plotting
    pressures = [row[2] for row in pressure_data]  # Pressure in Pa
    impulses = [row[3] for row in impulse_data]    # Impulse in Ns
    pressure_errors = [row[4] for row in pressure_data]  # Absolute uncertainty in Pa
    impulse_errors = [row[5] for row in impulse_data]    # Range in Ns
    
    # Atmospheric pressure (fixed point)
    atm_pressure = 1.016E+05  # Pa
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot data points with error bars
    ax.errorbar(pressures, impulses, xerr=pressure_errors, yerr=impulse_errors,
                fmt='ro', markersize=8, capsize=5, capthick=2, elinewidth=2,
                label='Experimental data', alpha=0.8)
    
    # Calculate best fit line (blue)
    slope, intercept, r_value, p_value, std_err = stats.linregress(pressures, impulses)
    
    # Create extended range for trend lines (including atmospheric pressure)
    x_min = atm_pressure
    x_max = max(pressures) * 1.1
    x_trend = np.linspace(x_min, x_max, 100)
    
    # Plot best fit line (blue)
    y_trend_fit = slope * x_trend + intercept
    ax.plot(x_trend, y_trend_fit, 'b-', linewidth=2, 
            label=f'Best fit: y = {slope:.2e}x + {intercept:.3f}\n(R² = {r_value**2:.4f})')
    
    # Calculate minimum and maximum lines that pass through all error bars
    # These lines are fixed at atmospheric pressure (x = 1.016E+05, y = 0)
    
    # Convert to numpy arrays for easier calculation
    pressures = np.array(pressures)
    impulses = np.array(impulses)
    pressure_errors = np.array(pressure_errors)
    impulse_errors = np.array(impulse_errors)
    
    # For each data point, calculate the range of slopes that would pass through its error rectangle
    # when the line is fixed at (atm_pressure, 0)
    min_slopes_allowed = []
    max_slopes_allowed = []
    
    for i in range(len(pressures)):
        # Define the error rectangle for this point
        p_min = pressures[i] - pressure_errors[i]
        p_max = pressures[i] + pressure_errors[i]
        i_min = impulses[i] - impulse_errors[i]
        i_max = impulses[i] + impulse_errors[i]
        
        # Calculate slopes from atmospheric pressure (atm_pressure, 0) to corners of error rectangle
        # Only consider corners that are to the right of atmospheric pressure
        slopes_for_this_point = []
        
        if p_min > atm_pressure:
            slopes_for_this_point.append(i_min / (p_min - atm_pressure))  # Bottom-left corner
            slopes_for_this_point.append(i_max / (p_min - atm_pressure))  # Top-left corner
        if p_max > atm_pressure:
            slopes_for_this_point.append(i_min / (p_max - atm_pressure))  # Bottom-right corner
            slopes_for_this_point.append(i_max / (p_max - atm_pressure))  # Top-right corner
        
        if slopes_for_this_point:
            min_slopes_allowed.append(min(slopes_for_this_point))
            max_slopes_allowed.append(max(slopes_for_this_point))
    
    # The minimum line must have a slope that is at least the maximum of all minimum slopes
    # The maximum line must have a slope that is at most the minimum of all maximum slopes
    min_slope = max(min_slopes_allowed) if min_slopes_allowed else 0
    max_slope = min(max_slopes_allowed) if max_slopes_allowed else slope * 2
    
    # Lines pass through (atm_pressure, 0), so y = slope * (x - atm_pressure)
    min_intercept = -min_slope * atm_pressure
    max_intercept = -max_slope * atm_pressure
    
    # Plot minimum and maximum lines
    y_trend_min = min_slope * x_trend + min_intercept
    y_trend_max = max_slope * x_trend + max_intercept
    
    ax.plot(x_trend, y_trend_min, 'g--', linewidth=2, alpha=0.7,
            label=f'Minimum fit: y = {min_slope:.2e}(x - {atm_pressure:.0e})')
    ax.plot(x_trend, y_trend_max, 'orange', linestyle='--', linewidth=2, alpha=0.7,
            label=f'Maximum fit: y = {max_slope:.2e}(x - {atm_pressure:.0e})')
    
    # Mark the atmospheric pressure point where lines intersect at y=0
    ax.plot(atm_pressure, 0, 'ko', markersize=8, label=f'Fixed point: ({atm_pressure:.0e}, 0)')
    ax.axvline(x=atm_pressure, color='purple', linestyle=':', alpha=0.5)
    
    # Formatting
    ax.set_xlabel('Pressure (Pa)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Impulse (Ns)', fontsize=12, fontweight='bold')
    ax.set_title('Pressure vs Impulse Relationship\nwith Min/Max Bounds Fixed at Atmospheric Pressure', 
                 fontsize=14, fontweight='bold')
    ax.legend(fontsize=9, loc='upper left')
    ax.grid(True, alpha=0.3)
    
    # Set axis limits
    ax.set_xlim(atm_pressure * 0.95, x_max)
    ax.set_ylim(0, max([i + e for i, e in zip(impulses, impulse_errors)]) * 1.1)
    
    # Format x-axis to show scientific notation
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    
    plt.tight_layout()
    plt.savefig('/workspaces/physics-ia/pressure_vs_impulse_updated.png', dpi=300, bbox_inches='tight')
    plt.savefig('/workspaces/physics-ia/pressure_vs_impulse_updated.pdf', bbox_inches='tight')
    plt.close()

def create_complete_measurements_table():
    """Create PNG of complete measurements table with all repetitions"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')
    
    # Headers - Peak Start, Peak End, and Peak Height
    headers = ['Pumps', 'Trial', 'Peak Start (s)', 'Peak End (s)', 'Peak Height (N)']
    
    # All measurement data organized by pumps (10 to 50)
    data = []
    
    # 10 pumps data
    starts_10 = ['3.8678', '2.3507', '1.5973', '2.1055', '2.2739']
    ends_10 = ['3.8821', '2.3630', '1.6063', '2.1473', '2.2986']
    heights_10 = ['14', '17', '16', '4', '5']
    
    for i in range(5):
        pump_label = '10' if i == 0 else ''  # Only show pump number on first row
        data.append([pump_label, f'Rep {i+1}', starts_10[i], ends_10[i], heights_10[i]])
    
    # 20 pumps data
    starts_20 = ['2.1416', '2.1203', '1.9926', '3.6033', '2.0122']
    ends_20 = ['2.1864', '2.1328', '2.0040', '3.6281', '2.0399']
    heights_20 = ['12', '17', '20', '17', '14']
    
    for i in range(5):
        pump_label = '20' if i == 0 else ''  # Only show pump number on first row
        data.append([pump_label, f'Rep {i+1}', starts_20[i], ends_20[i], heights_20[i]])
    
    # 30 pumps data
    starts_30 = ['2.9819', '1.8302', '2.6686', '4.0077', '4.6452']
    ends_30 = ['3.0025', '1.8451', '2.6769', '4.0328', '4.6890']
    heights_30 = ['24', '27', '24', '20', '11']
    
    for i in range(5):
        pump_label = '30' if i == 0 else ''  # Only show pump number on first row
        data.append([pump_label, f'Rep {i+1}', starts_30[i], ends_30[i], heights_30[i]])
    
    # 40 pumps data
    starts_40 = ['4.8642', '3.5060', '2.0100', '1.7300', '2.6613']
    ends_40 = ['4.9227', '3.5140', '2.0240', '1.7791', '2.6804']
    heights_40 = ['12', '40', '26', '12', '19']
    
    for i in range(5):
        pump_label = '40' if i == 0 else ''  # Only show pump number on first row
        data.append([pump_label, f'Rep {i+1}', starts_40[i], ends_40[i], heights_40[i]])
    
    # 50 pumps data
    starts_50 = ['2.5071', '2.3462', '2.1928', '3.0298', '2.6245']
    ends_50 = ['2.5843', '2.3567', '2.2020', '3.0876', '2.6689']
    heights_50 = ['19', '34', '32', '22', '30']
    
    for i in range(5):
        pump_label = '50' if i == 0 else ''  # Only show pump number on first row
        data.append([pump_label, f'Rep {i+1}', starts_50[i], ends_50[i], heights_50[i]])
    
    # Create table
    table = ax.table(cellText=data, colLabels=headers, 
                    cellLoc='center', loc='center',
                    colWidths=[0.15, 0.15, 0.25, 0.25, 0.2])
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2)
    
    # Style the table
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#E6E6FA')
        table[(0, i)].set_text_props(weight='bold')
    
    # Color rows by pump group
    colors = ['#F0F8FF', '#F8F8FF', '#F0FFF0', '#FFF8DC', '#FFE4E1']
    
    for i, row in enumerate(data):
        if row[0] == '10':
            color = colors[0]
        elif row[0] == '20':
            color = colors[1]
        elif row[0] == '30':
            color = colors[2]
        elif row[0] == '40':
            color = colors[3]
        elif row[0] == '50':
            color = colors[4]
        else:
            # Use the same color as the previous group
            if i < 5:
                color = colors[0]
            elif i < 10:
                color = colors[1]
            elif i < 15:
                color = colors[2]
            elif i < 20:
                color = colors[3]
            else:
                color = colors[4]
        
        for j in range(len(headers)):
            table[(i+1, j)].set_facecolor(color)
    
    plt.title('Complete Measurements: All Pump Amounts and Repetitions', 
              fontsize=14, fontweight='bold', pad=20)
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

if __name__ == "__main__":
    print("Creating final tables and graphs...")
    
    create_complete_measurements_table()
    print("✓ Created complete_measurements_table.png")
    
    create_pressure_table()
    print("✓ Created pressure_table_updated.png")
    
    create_impulse_table()
    print("✓ Created impulse_table_updated.png")
    
    create_updated_graph()
    print("✓ Created pressure_vs_impulse_updated.png and .pdf with blue best fit line and min/max bounds")
    
    print("\nAll final files created successfully!")
    print("- Blue line of best fit")
    print("- Minimum and maximum lines through error bars")
    print("- All lines fixed at atmospheric pressure (1.016E+05 Pa)")
