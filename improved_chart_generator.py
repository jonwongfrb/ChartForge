import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

class PCEChartGenerator:
    def __init__(self):
        self.default_colors = {
            'YoY_pce_headline': '#1f77b4',
            'YoY_pce_core': '#7cb342', 
            'YoY_pce_services': '#ff7f0e',
            'YoY_pce_goods': '#d62728'
        }
        
        self.default_labels = {
            'YoY_pce_headline': 'Headline',
            'YoY_pce_core': 'Core',
            'YoY_pce_services': 'Services',
            'YoY_pce_goods': 'Goods'
        }
    
    def read_csv(self, file_path):
        """Read and process CSV data"""
        df = pd.read_csv(file_path)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def get_series_data(self, df):
        """Extract individual series from dataframe"""
        series_data = {}
        keys = df['key'].unique()
        
        for key in keys:
            series_data[key] = df[df['key'] == key].copy().sort_values('date')
        
        return series_data, list(keys)
    
    def create_chart(self, df, title=None, custom_colors=None, custom_labels=None, 
                    show_table=True, from_date="2025-10", to_date="2025-11"):
        """Create chart matching PNG format exactly"""
        series_data, keys = self.get_series_data(df)
        
        # Use custom colors/labels if provided
        colors = custom_colors or self.default_colors
        labels = custom_labels or self.default_labels
        
        # Set up the plot with exact PNG dimensions
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot each series
        for i, key in enumerate(keys):
            series = series_data[key]
            color = colors.get(key, self.default_colors.get(key, f'C{i}'))
            label = labels.get(key, key.replace('_', ' ').title())
            
            ax.plot(series['date'], series['value'], 
                    color=color, linewidth=2.5, label=label)
        
        # Add 2% reference line
        ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)
        
        # Add COVID recession shading
        ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), 
                   alpha=0.3, color='gray')
        
        # Calculate dynamic y-axis range
        all_values = []
        for key in keys:
            all_values.extend(series_data[key]['value'].tolist())
        
        y_min = min(all_values)
        y_max = max(all_values)
        y_bottom = int(y_min) - 1 if y_min < 0 else 0
        y_top = max(8, int(y_max) + 1)
        
        # Format axes
        ax.set_ylim(y_bottom, y_top)
        ax.set_yticks(range(y_bottom, y_top + 1))
        ax.set_yticklabels([f'{i}%' for i in range(y_bottom, y_top + 1)])
        ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        
        # Add series labels directly on chart (first 3 series)
        label_positions = [
            (datetime(2021, 8, 1), 5.8),
            (datetime(2022, 6, 1), 4.5),
            (datetime(2023, 6, 1), 3.0)
        ]
        
        for i, key in enumerate(keys[:3]):
            if i < len(label_positions):
                pos_x, pos_y = label_positions[i]
                color = colors.get(key, f'C{i}')
                label = labels.get(key, key.replace('_', ' ').title())
                ax.text(pos_x, pos_y, label, fontsize=12, color=color, weight='bold')
        
        # Add data table if requested
        if show_table:
            self.add_data_table(ax, series_data, keys, labels, from_date, to_date)
        
        # Add title if provided
        if title:
            ax.set_title(title, fontsize=16, pad=20)
        
        # Style the chart
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def add_data_table(self, ax, series_data, keys, labels, from_date, to_date):
        """Add data table matching PNG format"""
        try:
            from_dt = pd.to_datetime(f"{from_date}-01")
            to_dt = pd.to_datetime(f"{to_date}-01")
            
            from_month = from_dt.strftime('%b %Y')
            to_month = to_dt.strftime('%b %Y')
            
            table_lines = [f"{from_month}  {to_month}   Chg."]
            
            for key in keys:
                series = series_data[key]
                
                # Find closest dates
                from_series = series[series['date'] <= from_dt].tail(1)
                to_series = series[series['date'] <= to_dt].tail(1)
                
                if not from_series.empty and not to_series.empty:
                    from_val = from_series.iloc[0]['value']
                    to_val = to_series.iloc[0]['value']
                    change = (to_val - from_val) * 100  # Convert to basis points
                    
                    label = labels.get(key, key.replace('_', ' ').title())
                    table_lines.append(f"{label:<8} {from_val:.3f}%     {to_val:.3f}%   {change:+.0f} b.p.")
            
            table_text = "\\n".join(table_lines)
            
            ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10,
                    verticalalignment='bottom', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        except Exception as e:
            print(f"Could not add data table: {e}")
    
    def export_python_script(self, df, output_path, custom_colors=None, custom_labels=None, 
                            title=None, from_date="2025-10", to_date="2025-11"):
        """Export standalone Python script with all customizations"""
        series_data, keys = self.get_series_data(df)
        colors = custom_colors or self.default_colors
        labels = custom_labels or self.default_labels
        
        script = f'''import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the CSV file (update path as needed)
df = pd.read_csv('your_data_file.csv')
df['date'] = pd.to_datetime(df['date'])

# Create plot
fig, ax = plt.subplots(figsize=(14, 8))

'''
        
        # Add plot commands for each series
        for key in keys:
            color = colors.get(key, '#1f77b4')
            label = labels.get(key, key.replace('_', ' ').title())
            script += f"# Plot {label}\\n"
            script += f"series = df[df['key'] == '{key}'].copy()\\n"
            script += f"ax.plot(series['date'], series['value'], color='{color}', linewidth=2.5, label='{label}')\\n\\n"
        
        script += '''# Add 2% reference line
ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)

# Add COVID recession shading
ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')

# Calculate dynamic y-axis
all_values = df['value'].tolist()
y_min, y_max = min(all_values), max(all_values)
y_bottom = max(0, int(y_min) - 1)
y_top = max(8, int(y_max) + 1)

# Format axes
ax.set_ylim(y_bottom, y_top)
ax.set_yticks(range(y_bottom, y_top + 1))
ax.set_yticklabels([f'{i}%' for i in range(y_bottom, y_top + 1)])
ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

'''
        
        # Add series labels
        label_positions = [
            (datetime(2021, 8, 1), 5.8),
            (datetime(2022, 6, 1), 4.5),
            (datetime(2023, 6, 1), 3.0)
        ]
        
        for i, key in enumerate(keys[:3]):
            if i < len(label_positions):
                pos_x, pos_y = label_positions[i]
                color = colors.get(key, '#1f77b4')
                label = labels.get(key, key.replace('_', ' ').title())
                script += f"ax.text(datetime({pos_x.year}, {pos_x.month}, {pos_x.day}), {pos_y}, '{label}', fontsize=12, color='{color}', weight='bold')\\n"
        
        # Add data table
        script += f'''
# Add data table
try:
    from_dt = pd.to_datetime("{from_date}-01")
    to_dt = pd.to_datetime("{to_date}-01")
    
    table_lines = ["{from_date}  {to_date}   Chg."]
    
'''
        
        for key in keys:
            label = labels.get(key, key.replace('_', ' ').title())
            script += f'''    series = df[df['key'] == '{key}']
    from_val = series[series['date'] <= from_dt].tail(1)['value'].iloc[0]
    to_val = series[series['date'] <= to_dt].tail(1)['value'].iloc[0]
    change = (to_val - from_val) * 100
    table_lines.append(f"{label:<8} {{from_val:.3f}}%     {{to_val:.3f}}%   {{change:+.0f}} b.p.")
    
'''
        
        script += '''    table_text = "\\\\n".join(table_lines)
    ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
except:
    pass

'''
        
        if title:
            script += f"ax.set_title('{title}', fontsize=16, pad=20)\\n"
        
        script += '''# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
'''
        
        with open(output_path, 'w') as f:
            f.write(script)
        
        print(f"Python script exported to: {output_path}")
    
    def save_chart(self, fig, output_path):
        """Save chart as PNG with high quality"""
        fig.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        print(f"Chart saved to: {output_path}")

# Example usage
if __name__ == "__main__":
    generator = PCEChartGenerator()
    
    # Read CSV file
    df = generator.read_csv('01a-YoY-PCE.csv')
    
    # Create chart with default settings
    fig = generator.create_chart(df)
    
    # Save chart
    generator.save_chart(fig, '01a-YoY-PCE-new.png')
    
    # Export Python script
    generator.export_python_script(df, 'exported_chart.py')
    
    plt.show()