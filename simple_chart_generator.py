import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def read_csv_data(file_path):
    """Read and process CSV data"""
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def get_series_data(df):
    """Extract individual series from dataframe"""
    series_data = {}
    keys = df['key'].unique()
    
    for key in keys:
        series_data[key] = df[df['key'] == key].copy()
    
    return series_data, keys

def create_chart(df, output_path=None):
    """Create chart matching PNG format"""
    series_data, keys = get_series_data(df)
    
    # Set up the plot
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Default colors
    colors = {'YoY_pce_headline': '#1f77b4', 'YoY_pce_core': '#7cb342'}
    labels = {'YoY_pce_headline': 'Headline', 'YoY_pce_core': 'Core'}
    
    # Plot each series
    for key in keys:
        series = series_data[key]
        color = colors.get(key, '#ff7f0e')
        label = labels.get(key, key.replace('_', ' ').title())
        
        ax.plot(series['date'], series['value'], 
                color=color, linewidth=2.5, label=label)
    
    # Add 2% reference line
    ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)
    
    # Add COVID recession shading
    ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), 
               alpha=0.3, color='gray')
    
    # Format axes
    ax.set_ylim(0, 8)
    ax.set_yticks(range(0, 9))
    ax.set_yticklabels([f'{i}%' for i in range(0, 9)])
    ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Add series labels on chart
    if 'YoY_pce_headline' in keys:
        ax.text(datetime(2021, 8, 1), 5.8, 'Headline', 
                fontsize=12, color='#1f77b4', weight='bold')
    if 'YoY_pce_core' in keys:
        ax.text(datetime(2022, 6, 1), 4.5, 'Core', 
                fontsize=12, color='#7cb342', weight='bold')
    
    # Add data table
    add_data_table(ax, series_data, keys)
    
    # Style the chart
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    return fig

def add_data_table(ax, series_data, keys):
    """Add data table to bottom right of chart"""
    if len(keys) < 2:
        return
    
    # Get latest two data points for each series
    table_lines = ["Oct 2025  Nov 2025   Chg."]
    
    for key in keys:
        series = series_data[key]
        if len(series) >= 2:
            latest_val = series.iloc[-1]['value']
            prev_val = series.iloc[-2]['value']
            change = (latest_val - prev_val) * 100  # Convert to basis points
            
            label = 'Headline' if 'headline' in key else 'Core' if 'core' in key else key
            table_lines.append(f"{label:<8} {prev_val:.3f}%     {latest_val:.3f}%   {change:+.0f} b.p.")
    
    table_text = "\n".join(table_lines)
    
    ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

def export_python_script(df, output_path):
    """Export standalone Python script"""
    series_data, keys = get_series_data(df)
    
    script = '''import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the CSV file
df = pd.read_csv('01a-YoY-PCE.csv')
df['date'] = pd.to_datetime(df['date'])

# Create plot
fig, ax = plt.subplots(figsize=(14, 8))

'''
    
    # Add plot commands for each series
    colors = {'YoY_pce_headline': '#1f77b4', 'YoY_pce_core': '#7cb342'}
    labels = {'YoY_pce_headline': 'Headline', 'YoY_pce_core': 'Core'}
    
    for key in keys:
        color = colors.get(key, '#ff7f0e')
        label = labels.get(key, key.replace('_', ' ').title())
        script += f"# Plot {label}\n"
        script += f"series = df[df['key'] == '{key}'].copy()\n"
        script += f"ax.plot(series['date'], series['value'], color='{color}', linewidth=2.5, label='{label}')\n\n"
    
    script += '''# Add 2% reference line
ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)

# Add COVID recession shading
ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')

# Format axes
ax.set_ylim(0, 8)
ax.set_yticks(range(0, 9))
ax.set_yticklabels([f'{i}%' for i in range(0, 9)])
ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Add series labels
ax.text(datetime(2021, 8, 1), 5.8, 'Headline', fontsize=12, color='#1f77b4', weight='bold')
ax.text(datetime(2022, 6, 1), 4.5, 'Core', fontsize=12, color='#7cb342', weight='bold')

# Add data table
table_text = """Oct 2025  Nov 2025   Chg.
Headline    2.678%     2.773%   +9 b.p.
Core        2.734%     2.791%   +6 b.p."""

ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10,
        verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
'''
    
    with open(output_path, 'w') as f:
        f.write(script)

# Example usage
if __name__ == "__main__":
    # Read CSV file
    df = read_csv_data('01a-YoY-PCE.csv')
    
    # Create chart
    fig = create_chart(df, '01a-YoY-PCE-generated.png')
    
    # Export Python script
    export_python_script(df, 'generated_chart.py')
    
    plt.show()