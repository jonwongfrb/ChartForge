import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PCEChartCustomizer:
    def __init__(self, root):
        self.root = root
        self.root.title("PCE Chart Customizer")
        self.root.geometry("1200x800")
        
        # Default colors for multiple series
        self.default_colors = ['#1f77b4', '#7cb342', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']
        self.series_colors = {}
        self.series_labels = {}
        self.legend_position = 'none'
        self.x_label = ''
        self.y_label = ''
        self.chart_title = ''
        
        self.df = None
        self.setup_ui()
    
    def setup_ui(self):
        # Control panel
        control_frame = ttk.Frame(self.root)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        # File loading
        ttk.Button(control_frame, text="Load CSV File", command=self.load_file).pack(pady=5)
        
        # Color controls
        ttk.Label(control_frame, text="Colors:").pack(pady=(10,0))
        ttk.Button(control_frame, text="Headline Color", command=self.choose_headline_color).pack(pady=2)
        ttk.Button(control_frame, text="Core Color", command=self.choose_core_color).pack(pady=2)
        
        # Label controls
        ttk.Label(control_frame, text="Labels:").pack(pady=(10,0))
        ttk.Label(control_frame, text="Headline Label:").pack()
        self.headline_entry = ttk.Entry(control_frame)
        self.headline_entry.insert(0, 'Headline')
        self.headline_entry.pack(pady=2)
        
        ttk.Label(control_frame, text="Core Label:").pack()
        self.core_entry = ttk.Entry(control_frame)
        self.core_entry.insert(0, 'Core')
        self.core_entry.pack(pady=2)
        
        # Legend position
        ttk.Label(control_frame, text="Legend Position:").pack(pady=(10,0))
        self.legend_var = tk.StringVar(value=self.legend_position)
        legend_combo = ttk.Combobox(control_frame, textvariable=self.legend_var, 
                                   values=['none', 'upper left', 'upper right', 'lower left', 'lower right', 'center'])
        legend_combo.pack(pady=2)
        
        # Axis labels
        ttk.Label(control_frame, text="X-axis Label:").pack(pady=(10,0))
        self.x_label_entry = ttk.Entry(control_frame)
        self.x_label_entry.pack(pady=2)
        
        ttk.Label(control_frame, text="Y-axis Label:").pack()
        self.y_label_entry = ttk.Entry(control_frame)
        self.y_label_entry.pack(pady=2)
        
        # Chart title
        ttk.Label(control_frame, text="Chart Title:").pack(pady=(10,0))
        self.title_entry = ttk.Entry(control_frame)
        self.title_entry.pack(pady=2)
        
        # Data table controls
        ttk.Label(control_frame, text="Data Table Range:").pack(pady=(10,0))
        
        # Show table checkbox
        self.show_table_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Show Data Table", variable=self.show_table_var).pack(pady=2)
        
        # Date range for table
        ttk.Label(control_frame, text="From Date (YYYY-MM):").pack()
        self.from_date_entry = ttk.Entry(control_frame)
        self.from_date_entry.insert(0, "2025-10")
        self.from_date_entry.pack(pady=2)
        
        ttk.Label(control_frame, text="To Date (YYYY-MM):").pack()
        self.to_date_entry = ttk.Entry(control_frame)
        self.to_date_entry.insert(0, "2025-11")
        self.to_date_entry.pack(pady=2)
        
        # Update button
        ttk.Button(control_frame, text="Update Chart", command=self.update_chart).pack(pady=10)
        
        # Revert button
        ttk.Button(control_frame, text="Revert to Original", command=self.revert_to_original).pack(pady=5)
        
        # Export script button
        ttk.Button(control_frame, text="Export Python Script", command=self.export_script).pack(pady=5)
        
        # Export R script button
        ttk.Button(control_frame, text="Export R Script", command=self.export_r_script).pack(pady=5)
        
        # Chart area
        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path)
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.create_original_chart()
    
    def revert_to_original(self):
        if self.df is None:
            return
        
        # Reset all values to defaults
        self.series_colors = {}
        self.series_labels = {}
        self.headline_entry.delete(0, tk.END)
        self.headline_entry.insert(0, 'Headline')
        self.core_entry.delete(0, tk.END)
        self.core_entry.insert(0, 'Core')
        self.legend_var.set('none')
        self.x_label_entry.delete(0, tk.END)
        self.y_label_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.show_table_var.set(True)
        self.from_date_entry.delete(0, tk.END)
        self.from_date_entry.insert(0, "2025-10")
        self.to_date_entry.delete(0, tk.END)
        self.to_date_entry.insert(0, "2025-11")
        
        # Show original chart
        self.create_original_chart()
    
    def export_script(self):
        if self.df is None:
            return
        
        # Get current settings
        series1, series2, key1, key2 = self.get_data_series()
        if series1 is None:
            return
            
        headline_label = self.headline_entry.get()
        core_label = self.core_entry.get()
        legend_pos = self.legend_var.get()
        x_label = self.x_label_entry.get()
        y_label = self.y_label_entry.get()
        chart_title = self.title_entry.get()
        show_table = self.show_table_var.get()
        from_date = self.from_date_entry.get()
        to_date = self.to_date_entry.get()
        
        # Generate script content
        script_content = f"""import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the CSV file (update path as needed)
df = pd.read_csv('your_data_file.csv')
df['date'] = pd.to_datetime(df['date'])

# Separate data
series1 = df[df['key'] == '{key1}'].copy()
series2 = df[df['key'] == '{key2}'].copy()

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))

# Plot lines
ax.plot(series1['date'], series1['value'], color='{self.headline_color}', 
        linewidth=2.5, label='{headline_label}')
ax.plot(series2['date'], series2['value'], color='{self.core_color}', 
        linewidth=2.5, label='{core_label}')

# Add 2% reference line
ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)

# Add COVID recession shading
ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')

# Formatting
ax.set_ylim(0, 8)
ax.set_yticks(range(0, 9))
ax.set_yticklabels([f'{{i}}%' for i in range(0, 9)])
ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Labels and title
"""
        
        if x_label:
            script_content += f"ax.set_xlabel('{x_label}')\n"
        if y_label:
            script_content += f"ax.set_ylabel('{y_label}')\n"
        if chart_title:
            script_content += f"ax.set_title('{chart_title}')\n"
            
        # Add line labels
        script_content += "\n# Add labels on the lines\n"
        if len(keys) >= 1:
            script_content += f"ax.text(datetime(2021, 8, 1), 5.8, '{self.series_labels[keys[0]]}', fontsize=12, color='{self.series_colors[keys[0]]}', weight='bold')\n"
        if len(keys) >= 2:
            script_content += f"ax.text(datetime(2022, 6, 1), 4.5, '{self.series_labels[keys[1]]}', fontsize=12, color='{self.series_colors[keys[1]]}', weight='bold')\n"
        if len(keys) >= 3:
            script_content += f"ax.text(datetime(2023, 6, 1), 3.0, '{self.series_labels[keys[2]]}', fontsize=12, color='{self.series_colors[keys[2]]}', weight='bold')\n"
        
        if legend_pos != 'none':
            script_content += f"ax.legend(loc='{legend_pos}')\n"
            
        if show_table:
            script_content += f"""\n# Add data table
try:
    from_date = "{from_date}-01"
    to_date = "{to_date}-01"
    
    s1_from = series1[series1['date'] == from_date]
    s1_to = series1[series1['date'] == to_date]
    s2_from = series2[series2['date'] == from_date]
    s2_to = series2[series2['date'] == to_date]
    
    if not (s1_from.empty or s1_to.empty or s2_from.empty or s2_to.empty):
        from_month = pd.to_datetime(from_date).strftime('%b %Y')
        to_month = pd.to_datetime(to_date).strftime('%b %Y')
        
        s1_from_val = s1_from.iloc[0]['value']
        s1_to_val = s1_to.iloc[0]['value']
        s2_from_val = s2_from.iloc[0]['value']
        s2_to_val = s2_to.iloc[0]['value']
        
        table_text = f\"\"\"{{from_month}}  {{to_month}}   Chg.
{headline_label}    {{s1_from_val:.2f}}%     {{s1_to_val:.2f}}%   {{(s1_to_val - s1_from_val)*100:.0f}} b.p.
{core_label}        {{s2_from_val:.2f}}%     {{s2_to_val:.2f}}%   {{(s2_to_val - s2_from_val)*100:.0f}} b.p.\"\"\"
        
        ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10, 
                verticalalignment='bottom', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
except:
    pass
"""
        
        script_content += """\n# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
"""
        
        # Save script
        import pandas as pd
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python files", "*.py")],
            title="Save Python Script"
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(script_content)
            print(f"Script exported to: {file_path}")
    
    def export_r_script(self):
        if self.df is None:
            return
        
        # Get current settings
        series1, series2, key1, key2 = self.get_data_series()
        if series1 is None:
            return
            
        headline_label = self.headline_entry.get()
        core_label = self.core_entry.get()
        legend_pos = self.legend_var.get()
        x_label = self.x_label_entry.get()
        y_label = self.y_label_entry.get()
        chart_title = self.title_entry.get()
        show_table = self.show_table_var.get()
        from_date = self.from_date_entry.get()
        to_date = self.to_date_entry.get()
        
        # Generate R script content
        script_content = f"""library(ggplot2)
library(dplyr)
library(lubridate)
library(scales)

# Read the CSV file (update path as needed)
df <- read.csv('your_data_file.csv')
df$date <- as.Date(df$date)

# Separate data
series1 <- df[df$key == '{key1}', ]
series2 <- df[df$key == '{key2}', ]

# Create plot
p <- ggplot() +
  geom_line(data = series1, aes(x = date, y = value, color = '{headline_label}'), size = 1.2) +
  geom_line(data = series2, aes(x = date, y = value, color = '{core_label}'), size = 1.2) +
  scale_color_manual(values = c('{headline_label}' = '{self.headline_color}', '{core_label}' = '{self.core_color}')) +
  geom_hline(yintercept = 2, linetype = 'dashed', color = 'black', alpha = 0.7) +
  annotate('rect', xmin = as.Date('2020-02-01'), xmax = as.Date('2020-04-01'), 
           ymin = -Inf, ymax = Inf, alpha = 0.3, fill = 'gray') +
  scale_y_continuous(limits = c(0, 8), breaks = 0:8, labels = paste0(0:8, '%')) +
  scale_x_date(limits = c(as.Date('2019-01-01'), as.Date('2026-01-01')), 
               date_breaks = '1 year', date_labels = '%Y') +
  theme_minimal() +
  theme(panel.grid.major = element_line(alpha = 0.3),
        panel.grid.minor = element_blank(),
        axis.line = element_line(color = 'black'),
        panel.border = element_blank())"""
        
        if x_label:
            script_content += f" +\n  xlab('{x_label}')"
        if y_label:
            script_content += f" +\n  ylab('{y_label}')"
        if chart_title:
            script_content += f" +\n  ggtitle('{chart_title}')"
            
        if legend_pos == 'none':
            script_content += " +\n  theme(legend.position = 'none')"
        else:
            legend_r = {'upper left': 'c(0.02, 0.98)', 'upper right': 'c(0.98, 0.98)', 
                       'lower left': 'c(0.02, 0.02)', 'lower right': 'c(0.98, 0.02)', 
                       'center': 'c(0.5, 0.5)'}
            script_content += f" +\n  theme(legend.position = {legend_r.get(legend_pos, 'c(0.02, 0.98)')})"
            
        script_content += "\n\n# Add text labels on lines\n"
        script_content += f"p <- p + annotate('text', x = as.Date('2021-08-01'), y = 5.8, label = '{headline_label}', \n                 color = '{self.headline_color}', fontface = 'bold', size = 4)\n"
        script_content += f"p <- p + annotate('text', x = as.Date('2022-06-01'), y = 4.5, label = '{core_label}', \n                 color = '{self.core_color}', fontface = 'bold', size = 4)\n"
        
        if show_table:
            script_content += f"""\n# Add data table
from_date <- as.Date('{from_date}-01')
to_date <- as.Date('{to_date}-01')

s1_from <- series1[series1$date == from_date, ]
s1_to <- series1[series1$date == to_date, ]
s2_from <- series2[series2$date == from_date, ]
s2_to <- series2[series2$date == to_date, ]

if(nrow(s1_from) > 0 & nrow(s1_to) > 0 & nrow(s2_from) > 0 & nrow(s2_to) > 0) {{
  from_month <- format(from_date, '%b %Y')
  to_month <- format(to_date, '%b %Y')
  
  s1_change <- (s1_to$value - s1_from$value) * 100
  s2_change <- (s2_to$value - s2_from$value) * 100
  
  table_text <- paste0(from_month, '  ', to_month, '   Chg.\n',
                      '{headline_label}    ', sprintf('%.2f', s1_from$value), '%     ', 
                      sprintf('%.2f', s1_to$value), '%   ', round(s1_change), ' b.p.\n',
                      '{core_label}        ', sprintf('%.2f', s2_from$value), '%     ', 
                      sprintf('%.2f', s2_to$value), '%   ', round(s2_change), ' b.p.')
  
  p <- p + annotate('text', x = as.Date('2025-06-01'), y = 0.5, label = table_text, 
                   hjust = 1, vjust = 0, size = 3, 
                   color = 'black', fontface = 'plain')
}}"""
        
        script_content += "\n\n# Display plot\nprint(p)\n"
        
        # Save script
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            defaultextension=".R",
            filetypes=[("R files", "*.R")],
            title="Save R Script"
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(script_content)
            print(f"R script exported to: {file_path}")
    
    def choose_headline_color(self):
        color = colorchooser.askcolor(title="Choose Headline Color")[1]
        if color and len(self.series_colors) > 0:
            keys = list(self.series_colors.keys())
            self.series_colors[keys[0]] = color
    
    def choose_core_color(self):
        color = colorchooser.askcolor(title="Choose Core Color")[1]
        if color and len(self.series_colors) > 1:
            keys = list(self.series_colors.keys())
            self.series_colors[keys[1]] = color
    
    def detect_data_keys(self):
        """Auto-detect all data series keys from CSV"""
        if self.df is None:
            return []
        
        unique_keys = self.df['key'].unique()
        return list(unique_keys)
    
    def get_all_data_series(self):
        """Get all data series based on detected keys"""
        keys = self.detect_data_keys()
        series_data = {}
        
        for i, key in enumerate(keys):
            series = self.df[self.df['key'] == key].copy()
            series_data[key] = series
            
            # Set default colors and labels
            if key not in self.series_colors:
                self.series_colors[key] = self.default_colors[i % len(self.default_colors)]
            if key not in self.series_labels:
                # Create friendly label from key
                label = key.replace('YoY_pce_', '').replace('MoM_pce_', '').replace('_pce_', '').replace('_', ' ').title()
                if not label:  # If empty after replacements
                    label = key.replace('_', ' ').title()
                self.series_labels[key] = label
                
        return series_data, keys
    
    def create_original_chart(self):
        """Create the exact original chart matching the PNG"""
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Separate data using auto-detection
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
        
        # Create plot with original styling
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot all series
        for i, key in enumerate(keys):
            series = series_data[key]
            color = self.series_colors[key]
            label = self.series_labels[key]
            ax.plot(series['date'], series['value'], color=color, linewidth=2.5, label=label)
        
        # Add 2% reference line
        ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)
        
        # Add COVID recession shading
        ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')
        
        # Original formatting
        ax.set_ylim(0, 8)
        ax.set_yticks(range(0, 9))
        ax.set_yticklabels([f'{i}%' for i in range(0, 9)])
        ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        
        # Add original labels on lines (first three series)
        if len(keys) >= 1:
            first_series = series_data[keys[0]]
            ax.text(datetime(2021, 8, 1), 5.8, self.series_labels[keys[0]], 
                   fontsize=12, color=self.series_colors[keys[0]], weight='bold')
        if len(keys) >= 2:
            second_series = series_data[keys[1]]
            ax.text(datetime(2022, 6, 1), 4.5, self.series_labels[keys[1]], 
                   fontsize=12, color=self.series_colors[keys[1]], weight='bold')
        if len(keys) >= 3:
            third_series = series_data[keys[2]]
            ax.text(datetime(2023, 6, 1), 3.0, self.series_labels[keys[2]], 
                   fontsize=12, color=self.series_colors[keys[2]], weight='bold')
        
        # Add original data table (all series)
        if len(keys) >= 2:
            table_lines = ["Oct 2025  Nov 2025   Chg."]
            
            for key in keys:
                series = series_data[key]
                latest_val = series.iloc[-1]['value']
                prev_val = series.iloc[-2]['value']
                change = (latest_val - prev_val) * 100
                
                label = self.series_labels[key]
                table_lines.append(f"{label:<12} {prev_val:.2f}%     {latest_val:.2f}%   {change:.0f} b.p.")
            
            table_text = "\n".join(table_lines)
            
            ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10, 
                    verticalalignment='bottom', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Original style
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Add to GUI
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def update_chart(self):
        if self.df is None:
            return
        
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Get current values
        self.headline_label = self.headline_entry.get()
        self.core_label = self.core_entry.get()
        self.legend_position = self.legend_var.get()
        self.x_label = self.x_label_entry.get()
        self.y_label = self.y_label_entry.get()
        self.chart_title = self.title_entry.get()
        
        # Separate data using auto-detection
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot all series
        for key in keys:
            series = series_data[key]
            color = self.series_colors[key]
            label = self.series_labels[key]
            ax.plot(series['date'], series['value'], color=color, 
                    linewidth=2.5, label=label)
        
        # Add 2% reference line
        ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)
        
        # Add COVID recession shading
        ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')
        
        # Formatting
        ax.set_ylim(0, 8)
        ax.set_yticks(range(0, 9))
        ax.set_yticklabels([f'{i}%' for i in range(0, 9)])
        ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        
        # Labels and title
        if self.x_label:
            ax.set_xlabel(self.x_label)
        if self.y_label:
            ax.set_ylabel(self.y_label)
        if self.chart_title:
            ax.set_title(self.chart_title)
        
        # Add labels on the lines (first three series)
        if len(keys) >= 1:
            ax.text(datetime(2021, 8, 1), 5.8, self.series_labels[keys[0]], 
                   fontsize=12, color=self.series_colors[keys[0]], weight='bold')
        if len(keys) >= 2:
            ax.text(datetime(2022, 6, 1), 4.5, self.series_labels[keys[1]], 
                   fontsize=12, color=self.series_colors[keys[1]], weight='bold')
        if len(keys) >= 3:
            ax.text(datetime(2023, 6, 1), 3.0, self.series_labels[keys[2]], 
                   fontsize=12, color=self.series_colors[keys[2]], weight='bold')
        
        # Legend (optional - can be hidden by setting position to 'none')
        if self.legend_position != 'none':
            ax.legend(loc=self.legend_position)
        
        # Add data table if enabled
        if self.show_table_var.get():
            self.add_data_table(ax, series_data, keys)
        
        # Style
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3)
        
        # Add to GUI
        canvas = FigureCanvasTkAgg(fig, self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def add_data_table(self, ax, series_data, keys):
        """Add customizable data table to chart"""
        if len(keys) < 2:
            return
            
        try:
            from_date = self.from_date_entry.get() + "-01"
            to_date = self.to_date_entry.get() + "-01"
            
            table_lines = []
            from_month = pd.to_datetime(from_date).strftime('%b %Y')
            to_month = pd.to_datetime(to_date).strftime('%b %Y')
            table_lines.append(f"{from_month}  {to_month}   Chg.")
            
            # Add all series to table
            for key in keys:
                series = series_data[key]
                s_from = series[series['date'] == from_date]
                s_to = series[series['date'] == to_date]
                
                if not (s_from.empty or s_to.empty):
                    s_from_val = s_from.iloc[0]['value']
                    s_to_val = s_to.iloc[0]['value']
                    change = (s_to_val - s_from_val) * 100
                    
                    label = self.series_labels[key]
                    table_lines.append(f"{label:<12} {s_from_val:.2f}%     {s_to_val:.2f}%   {change:.0f} b.p.")
            
            if len(table_lines) > 1:
                table_text = "\n".join(table_lines)
                ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10, 
                        verticalalignment='bottom', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        except:
            pass  # Skip table if date format is invalid

if __name__ == "__main__":
    root = tk.Tk()
    app = PCEChartCustomizer(root)
    root.mainloop()