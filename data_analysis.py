import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import re

# Parse the data from the file
def parse_data():
    with open('tabbele data', 'r') as file:
        content = file.read()
    
    # Extract pressure data (first section)
    pressure_data = {
        'pumps': [0, 10, 20, 30, 40, 50],
        'volume': [0.000250, 0.000630, 0.001010, 0.001390, 0.001770, 0.002150],
        'pressure_pa': [1.016E+05, 2.560E+05, 4.105E+05, 5.649E+05, 7.193E+05, 8.738E+05],
        'relative_uncertainty': [0.40, 3.29, 3.16, 3.12, 3.10, 3.08]  # in %
    }
    
    # Calculate absolute pressure uncertainty
    pressure_data['pressure_uncertainty'] = [
        pressure_data['pressure_pa'][i] * pressure_data['relative_uncertainty'][i] / 100 
        for i in range(len(pressure_data['pumps']))
    ]
    
    # Extract impulse data (final section)
    impulse_data = {
        'pumps': [50, 40, 30, 20, 10],
        'change_in_time': [0.0398, 0.0297, 0.0225, 0.0242, 0.0204],
        'peak_height': [27, 22, 21, 16, 11],
        'impulse_ns': [0.55, 0.32, 0.24, 0.19, 0.11],
        'uncertainty_percent': [4.15, 5.26, 5.60, 7.08, 9.91],
        'ranges_ns': [0.29, 0.10, 0.07, 0.08, 0.02]
    }
    
    return pressure_data, impulse_data

def create_tables():
    pressure_data, impulse_data = parse_data()
    
    # Create pressure table
    pressure_df = pd.DataFrame({
        'Pumps': pressure_data['pumps'],
        'Volume (m³)': [f"{v:.6f} ± 0.000002" for v in pressure_data['volume']],
        'Pressure (Pa)': [f"{p:.2E}" for p in pressure_data['pressure_pa']],
        'Relative Uncertainty (%)': [f"{u:.2f}" for u in pressure_data['relative_uncertainty']],
        'Absolute Uncertainty (Pa)': [f"{u:.0f}" for u in pressure_data['pressure_uncertainty']]
    })
    
    # Create impulse table
    impulse_df = pd.DataFrame({
        'Pumps': impulse_data['pumps'],
        'Change in Time (s)': impulse_data['change_in_time'],
        'Peak Height (N)': impulse_data['peak_height'],
        'Impulse (Ns)': impulse_data['impulse_ns'],
        'Uncertainty (%)': impulse_data['uncertainty_percent'],
        'Range (Ns)': impulse_data['ranges_ns']
    })
    
    print("PRESSURE DATA TABLE")
    print("=" * 80)
    print(pressure_df.to_string(index=False))
    print("\n")
    
    print("IMPULSE DATA TABLE")
    print("=" * 80)
    print(impulse_df.to_string(index=False))
    print("\n")
    
    return pressure_df, impulse_df

def create_combined_data():
    pressure_data, impulse_data = parse_data()
    
    # Match data by pump number (excluding 0 pumps from pressure data)
    combined_data = []
    for pump in impulse_data['pumps']:
        if pump in pressure_data['pumps']:
            p_idx = pressure_data['pumps'].index(pump)
            i_idx = impulse_data['pumps'].index(pump)
            
            combined_data.append({
                'pumps': pump,
                'pressure': pressure_data['pressure_pa'][p_idx],
                'pressure_uncertainty': pressure_data['pressure_uncertainty'][p_idx],
                'impulse': impulse_data['impulse_ns'][i_idx],
                'impulse_range': impulse_data['ranges_ns'][i_idx]
            })
    
    return combined_data

def create_graph():
    combined_data = create_combined_data()
    
    # Extract data for plotting
    pressures = [d['pressure'] for d in combined_data]
    pressure_errors = [d['pressure_uncertainty'] for d in combined_data]
    impulses = [d['impulse'] for d in combined_data]
    impulse_errors = [d['impulse_range'] for d in combined_data]
    pump_labels = [str(d['pumps']) for d in combined_data]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot data points with error bars
    scatter = ax.errorbar(pressures, impulses, 
                         xerr=pressure_errors, 
                         yerr=impulse_errors,
                         fmt='o', 
                         markersize=8, 
                         capsize=5, 
                         capthick=2,
                         elinewidth=2,
                         markerfacecolor='blue',
                         markeredgecolor='darkblue',
                         ecolor='red',
                         alpha=0.7,
                         label='Data points')
    
    # Add labels for each point
    for i, (x, y, label) in enumerate(zip(pressures, impulses, pump_labels)):
        ax.annotate(f'{label} pumps', 
                   (x, y), 
                   xytext=(10, 10), 
                   textcoords='offset points',
                   fontsize=9,
                   ha='left')
    
    # Calculate and plot trend line
    slope, intercept, r_value, p_value, std_err = stats.linregress(pressures, impulses)
    
    # Calculate trend line through origin (forced intercept = 0)
    # Using least squares with no intercept: slope_origin = sum(xy) / sum(x²)
    pressures_array = np.array(pressures)
    impulses_array = np.array(impulses)
    slope_origin = np.sum(pressures_array * impulses_array) / np.sum(pressures_array ** 2)
    
    # Calculate R² for line through origin
    y_pred_origin = slope_origin * pressures_array
    ss_res_origin = np.sum((impulses_array - y_pred_origin) ** 2)
    ss_tot_origin = np.sum((impulses_array - np.mean(impulses_array)) ** 2)
    r_squared_origin = 1 - (ss_res_origin / ss_tot_origin)
    
    # Generate trend line points starting from origin
    x_trend = np.linspace(0, max(pressures), 100)
    y_trend = slope * x_trend + intercept
    y_trend_origin = slope_origin * x_trend
    
    # Plot both trend lines
    ax.plot(x_trend, y_trend, 'r--', linewidth=2, 
            label=f'Best fit: y = {slope:.2e}x + {intercept:.3f}\nR² = {r_value**2:.4f}')
    ax.plot(x_trend, y_trend_origin, 'g-', linewidth=2, 
            label=f'Through origin: y = {slope_origin:.2e}x\nR² = {r_squared_origin:.4f}')
    
    # Set axis limits to show origin
    ax.set_xlim(0, max(pressures) * 1.1)
    ax.set_ylim(0, max(impulses) * 1.1)
    
    # Formatting
    ax.set_xlabel('Pressure /Pa', fontsize=12, fontweight='bold')
    ax.set_ylabel('Impulse /Ns', fontsize=12, fontweight='bold')
    ax.set_title('Pressure vs Impulse with Error Bars and Trend Lines', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Scientific notation for x-axis
    ax.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
    
    # Grid
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # Legend
    ax.legend(loc='upper left', fontsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the figure
    plt.savefig('pressure_vs_impulse.png', dpi=300, bbox_inches='tight')
    plt.savefig('pressure_vs_impulse.pdf', bbox_inches='tight')
    
    # Show statistics
    print("GRAPH STATISTICS")
    print("=" * 40)
    print(f"Best fit line equation: y = {slope:.2e}x + {intercept:.3f}")
    print(f"Line through origin equation: y = {slope_origin:.2e}x")
    print(f"Best fit R²: {r_value**2:.4f}")
    print(f"Through origin R²: {r_squared_origin:.4f}")
    print(f"Correlation coefficient (r): {r_value:.4f}")
    print(f"P-value: {p_value:.2e}")
    print(f"Standard error: {std_err:.2e}")
    print("\n")
    
    plt.show()
    
    return slope, intercept, r_value, slope_origin, r_squared_origin

def create_combined_table():
    combined_data = create_combined_data()
    
    # Create combined table
    combined_df = pd.DataFrame({
        'Pumps': [d['pumps'] for d in combined_data],
        'Pressure (Pa)': [f"{d['pressure']:.2E} ± {d['pressure_uncertainty']:.0f}" for d in combined_data],
        'Impulse (Ns)': [f"{d['impulse']:.2f} ± {d['impulse_range']:.2f}" for d in combined_data]
    })
    
    print("COMBINED PRESSURE VS IMPULSE TABLE")
    print("=" * 60)
    print(combined_df.to_string(index=False))
    print("\n")
    
    return combined_df

if __name__ == "__main__":
    print("PHYSICS IA DATA ANALYSIS")
    print("=" * 50)
    print()
    
    # Create and display tables
    pressure_df, impulse_df = create_tables()
    combined_df = create_combined_table()
    
    # Create and display graph
    slope, intercept, r_value, slope_origin, r_squared_origin = create_graph()
    
    print("Analysis complete!")
    print("Generated files:")
    print("- pressure_vs_impulse.png")
    print("- pressure_vs_impulse.pdf")
