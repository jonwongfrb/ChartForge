import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages

class PCEChartCustomizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Charting Assistant")
        self.root.geometry("1200x800")
        
        # Default colors for multiple series
        self.default_colors = ['#1f77b4', '#7cb342', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']
        self.series_colors = {}
        self.series_labels = {}
        self.label_entries = {}
        self.color_buttons = {}
        self.legend_position = 'none'
        self.x_label = ''
        self.y_label = ''
        self.chart_title = ''
        self.current_view = 'export'  # Track current view
        
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
        
        # Dynamic color buttons based on detected series
        self.color_buttons_frame = ttk.Frame(control_frame)
        self.color_buttons_frame.pack(pady=2)
        
        # Placeholder buttons (will be updated when file loads)
        ttk.Button(self.color_buttons_frame, text="Series 1 Color", command=self.choose_headline_color).pack(pady=2)
        ttk.Button(self.color_buttons_frame, text="Series 2 Color", command=self.choose_core_color).pack(pady=2)
        
        # Label controls
        ttk.Label(control_frame, text="Labels:").pack(pady=(10,0))
        
        # Dynamic label entries based on detected series
        self.label_entries = {}
        self.label_frame = ttk.Frame(control_frame)
        self.label_frame.pack(pady=2)
        
        # Placeholder entries (will be updated when file loads)
        ttk.Label(self.label_frame, text="Series 1 Label:").pack()
        self.headline_entry = ttk.Entry(self.label_frame)
        self.headline_entry.insert(0, 'Headline')
        self.headline_entry.pack(pady=2)
        
        ttk.Label(self.label_frame, text="Series 2 Label:").pack()
        self.core_entry = ttk.Entry(self.label_frame)
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
        
        # View toggle
        ttk.Label(control_frame, text="Chart View:").pack(pady=(10,0))
        self.view_var = tk.StringVar(value="export")
        ttk.Radiobutton(control_frame, text="Export Preview", variable=self.view_var, 
                       value="export", command=self.toggle_view).pack()
        ttk.Radiobutton(control_frame, text="Customized View", variable=self.view_var, 
                       value="custom", command=self.toggle_view).pack()
        
        # Revert button
        ttk.Button(control_frame, text="Revert to Original", command=self.revert_to_original).pack(pady=5)
        
        # Export script button
        ttk.Button(control_frame, text="Export Python Script", command=self.export_script).pack(pady=5)
        
        # Export R script button
        ttk.Button(control_frame, text="Export R Script", command=self.export_r_script).pack(pady=5)
        
        # Export image buttons
        ttk.Button(control_frame, text="Export PNG", command=self.export_png).pack(pady=5)
        ttk.Button(control_frame, text="Export PDF", command=self.export_pdf).pack(pady=5)
        
        # Analytics button
        ttk.Button(control_frame, text="Generate Analytics", command=self.show_analytics).pack(pady=10)
        
        # Chart area
        self.chart_frame = ttk.Frame(self.root)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.df = pd.read_csv(file_path)
            self.df['date'] = pd.to_datetime(self.df['date'])
            print(f"Detected keys: {self.detect_data_keys()}")  # Debug
            self.update_label_controls()
            self.create_original_chart()
    
    def toggle_view(self):
        """Toggle between export preview and customized view"""
        if self.df is None:
            return
        
        self.current_view = self.view_var.get()
        if self.current_view == "export":
            self.create_original_chart()
        else:
            self.update_chart()
    
    def update_label_controls(self):
        """Update label controls based on detected series"""
        # Clear existing label controls
        for widget in self.label_frame.winfo_children():
            widget.destroy()
        
        # Clear existing color controls
        for widget in self.color_buttons_frame.winfo_children():
            widget.destroy()
        
        # Get detected keys
        keys = self.detect_data_keys()
        self.label_entries = {}
        self.color_buttons = {}
        
        # Create entry and color button for each series
        for i, key in enumerate(keys):
            label_name = key.replace('YoY_pce_', '').replace('MoM_pce_', '').replace('_pce_', '').replace('_', ' ').title()
            if not label_name:
                label_name = key.replace('_', ' ').title()
            
            # Label entry
            ttk.Label(self.label_frame, text=f"{label_name} Label:").pack()
            entry = ttk.Entry(self.label_frame)
            entry.insert(0, label_name)
            entry.pack(pady=2)
            self.label_entries[key] = entry
            
            # Color button
            color_button = ttk.Button(self.color_buttons_frame, text=f"{label_name} Color", 
                                    command=lambda k=key: self.choose_series_color(k))
            color_button.pack(pady=2)
            self.color_buttons[key] = color_button
        
        # Keep references for backward compatibility
        if len(keys) >= 1:
            self.headline_entry = self.label_entries[keys[0]]
        if len(keys) >= 2:
            self.core_entry = self.label_entries[keys[1]]
    
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
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
            
        # Update labels from UI
        for key in keys:
            if hasattr(self, 'label_entries') and key in self.label_entries:
                self.series_labels[key] = self.label_entries[key].get()
        
        legend_pos = self.legend_var.get()
        x_label = self.x_label_entry.get()
        y_label = self.y_label_entry.get()
        chart_title = self.title_entry.get()
        show_table = self.show_table_var.get()
        from_date = self.from_date_entry.get()
        to_date = self.to_date_entry.get()
        
        # Generate script content
        script_content = """import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the CSV file (update path as needed)
df = pd.read_csv('your_data_file.csv')
df['date'] = pd.to_datetime(df['date'])

# Create plot
fig, ax = plt.subplots(figsize=(10, 6))

"""
        
        # Add plot lines for all series
        for key in keys:
            color = self.series_colors[key]
            label = self.series_labels[key]
            script_content += f"# Plot {label}\n"
            script_content += f"series = df[df['key'] == '{key}'].copy()\n"
            script_content += f"ax.plot(series['date'], series['value'], color='{color}', linewidth=2.5, label='{label}')\n\n"
        
        script_content += """# Add 2% reference line
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
            script_content += f"\nax.legend(loc='{legend_pos}')\n"
            
        script_content += """\n# Style
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
"""
        
        # Save script
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
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
            
        # Update labels from UI
        for key in keys:
            if hasattr(self, 'label_entries') and key in self.label_entries:
                self.series_labels[key] = self.label_entries[key].get()
        
        legend_pos = self.legend_var.get()
        x_label = self.x_label_entry.get()
        y_label = self.y_label_entry.get()
        chart_title = self.title_entry.get()
        
        # Generate R script content
        script_content = """library(ggplot2)
library(dplyr)
library(lubridate)
library(scales)

# Read the CSV file (update path as needed)
df <- read.csv('your_data_file.csv')
df$date <- as.Date(df$date)

# Create plot
p <- ggplot()
"""
        
        # Add geom_line for each series
        colors_r = []
        for key in keys:
            color = self.series_colors[key]
            label = self.series_labels[key]
            script_content += f"p <- p + geom_line(data = df[df$key == '{key}', ], aes(x = date, y = value, color = '{label}'), size = 1.2)\n"
            colors_r.append(f"'{label}' = '{color}'")
        
        script_content += f"\np <- p + scale_color_manual(values = c({', '.join(colors_r)}))\n"
        
        script_content += """ +
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
        panel.border = element_blank())

"""
        
        if x_label:
            script_content += f" +\n  xlab('{x_label}')"
        if y_label:
            script_content += f" +\n  ylab('{y_label}')"
        if chart_title:
            script_content += f" +\n  ggtitle('{chart_title}')"
            
        if legend_pos == 'none':
            script_content += " +\n  theme(legend.position = 'none')"
        
        script_content += "\n\n# Display plot\nprint(p)\n"
        
        # Save script
        file_path = filedialog.asksaveasfilename(
            defaultextension=".R",
            filetypes=[("R files", "*.R")],
            title="Save R Script"
        )
        
        if file_path:
            with open(file_path, 'w') as f:
                f.write(script_content)
            print(f"R script exported to: {file_path}")
    
    def choose_series_color(self, key):
        """Choose color for any series"""
        label_name = self.series_labels.get(key, key)
        color = colorchooser.askcolor(title=f"Choose {label_name} Color")[1]
        if color:
            self.series_colors[key] = color
    
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
        """Create the exact original chart matching the PNG (Export Preview)"""
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        # Add title label
        title_label = ttk.Label(self.chart_frame, text="Export Preview (PNG/PDF will look like this)", 
                               font=('Arial', 10, 'bold'))
        title_label.pack(pady=5)
        
        # Separate data using auto-detection
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
        
        # Create the export chart
        fig = self._create_export_chart(series_data, keys)
        
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
        
        # Add title label
        title_label = ttk.Label(self.chart_frame, text="Customized View (with your modifications)", 
                               font=('Arial', 10, 'bold'))
        title_label.pack(pady=5)
        
        # Get current values
        self.legend_position = self.legend_var.get()
        self.x_label = self.x_label_entry.get()
        self.y_label = self.y_label_entry.get()
        self.chart_title = self.title_entry.get()
        
        # Update labels from UI
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
        
        # Update all series labels from their respective entries
        for key in keys:
            if key in self.label_entries:
                self.series_labels[key] = self.label_entries[key].get()
        
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
        
        # Formatting with dynamic y-axis
        all_values = []
        for key in keys:
            series = series_data[key]
            all_values.extend(series['value'].tolist())
        
        y_min = min(all_values)
        y_max = max(all_values)
        
        # Set y-axis limits with some padding
        if y_min < 0:
            y_bottom = int(y_min) - 1
        else:
            y_bottom = 0
        y_top = max(8, int(y_max) + 1)
        
        ax.set_ylim(y_bottom, y_top)
        ax.set_yticks(range(y_bottom, y_top + 1))
        ax.set_yticklabels([f'{i}%' for i in range(y_bottom, y_top + 1)])
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
            ax.text(datetime(2023, 6, 1), 2.0, self.series_labels[keys[2]], 
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
                    change = (s_to_val - s_from_val) * 100  # Convert to basis points
                    
                    label = self.series_labels[key]
                    table_lines.append(f"{label:<8} {s_from_val:.3f}%     {s_to_val:.3f}%   {change:+.0f} b.p.")
            
            if len(table_lines) > 1:
                table_text = "\n".join(table_lines)
                ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10, 
                        verticalalignment='bottom', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        except:
            pass  # Skip table if date format is invalid
    
    def show_analytics(self):
        """Generate and display analytics summary"""
        if self.df is None:
            return
        
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
        
        # Create analytics window
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Data Analytics Summary")
        analytics_window.geometry("600x500")
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(analytics_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Generate analytics
        summary = self.generate_analytics(series_data, keys)
        text_widget.insert('1.0', summary)
        text_widget.config(state=tk.DISABLED)
    
    def generate_analytics(self, series_data, keys):
        """Generate comprehensive analytics summary"""
        summary = "DATA ANALYTICS SUMMARY\n"
        summary += "=" * 50 + "\n\n"
        
        for key in keys:
            series = series_data[key]
            label = self.series_labels[key]
            values = series['value'].values
            
            summary += f"{label.upper()}\n"
            summary += "-" * 30 + "\n"
            
            # Basic statistics
            summary += f"Current Value: {values[-1]:.2f}%\n"
            summary += f"Mean: {values.mean():.2f}%\n"
            summary += f"Median: {pd.Series(values).median():.2f}%\n"
            summary += f"Min: {values.min():.2f}% ({series[series['value'] == values.min()]['date'].iloc[0].strftime('%b %Y')})\n"
            summary += f"Max: {values.max():.2f}% ({series[series['value'] == values.max()]['date'].iloc[0].strftime('%b %Y')})\n"
            summary += f"Std Dev: {values.std():.2f}%\n"
            
            # Trend analysis
            recent_6m = values[-6:]
            recent_12m = values[-12:]
            summary += f"\n6-Month Avg: {recent_6m.mean():.2f}%\n"
            summary += f"12-Month Avg: {recent_12m.mean():.2f}%\n"
            
            # Change analysis
            mom_change = (values[-1] - values[-2]) * 100
            yoy_change = (values[-1] - values[-12]) * 100 if len(values) >= 12 else 0
            summary += f"\nMonth-over-Month Change: {mom_change:+.0f} b.p.\n"
            if len(values) >= 12:
                summary += f"Year-over-Year Change: {yoy_change:+.0f} b.p.\n"
            
            # Volatility
            summary += f"\nVolatility (Std Dev): {values.std():.2f}%\n"
            
            # Above/Below 2% target
            above_2 = (values > 2).sum()
            below_2 = (values <= 2).sum()
            summary += f"\nMonths Above 2%: {above_2} ({above_2/len(values)*100:.1f}%)\n"
            summary += f"Months At/Below 2%: {below_2} ({below_2/len(values)*100:.1f}%)\n"
            
            summary += "\n" + "=" * 50 + "\n\n"
        
        # Comparative analysis if multiple series
        if len(keys) >= 2:
            summary += "COMPARATIVE ANALYSIS\n"
            summary += "=" * 50 + "\n"
            
            for i in range(len(keys)):
                for j in range(i+1, len(keys)):
                    key1, key2 = keys[i], keys[j]
                    label1, label2 = self.series_labels[key1], self.series_labels[key2]
                    
                    val1 = series_data[key1]['value'].values[-1]
                    val2 = series_data[key2]['value'].values[-1]
                    spread = (val1 - val2) * 100
                    
                    summary += f"\n{label1} vs {label2}:\n"
                    summary += f"Current Spread: {spread:+.0f} b.p.\n"
                    summary += f"{label1}: {val1:.2f}%\n"
                    summary += f"{label2}: {val2:.2f}%\n"
        
        return summary
    
    def export_png(self):
        """Export current chart as PNG"""
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return
        
        # Get current settings
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
        
        # Update labels from UI
        for key in keys:
            if key in self.label_entries:
                self.series_labels[key] = self.label_entries[key].get()
        
        # Create the chart
        fig = self._create_export_chart(series_data, keys)
        
        # Save as PNG
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            title="Save Chart as PNG"
        )
        
        if file_path:
            fig.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close(fig)
            messagebox.showinfo("Success", f"Chart exported to: {file_path}")
    
    def export_pdf(self):
        """Export current chart as PDF"""
        if self.df is None:
            messagebox.showwarning("No Data", "Please load a CSV file first.")
            return
        
        # Get current settings
        series_data, keys = self.get_all_data_series()
        if not series_data:
            return
        
        # Update labels from UI
        for key in keys:
            if key in self.label_entries:
                self.series_labels[key] = self.label_entries[key].get()
        
        # Create the chart
        fig = self._create_export_chart(series_data, keys)
        
        # Save as PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Chart as PDF"
        )
        
        if file_path:
            with PdfPages(file_path) as pdf:
                pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            messagebox.showinfo("Success", f"Chart exported to: {file_path}")
    
    def _create_export_chart(self, series_data, keys):
        """Create chart for export that matches the original image exactly"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Plot all series
        for key in keys:
            series = series_data[key]
            color = self.series_colors[key]
            label = self.series_labels[key]
            ax.plot(series['date'], series['value'], color=color, linewidth=2.5, label=label)
        
        # Add 2% reference line
        ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)
        
        # Add COVID recession shading
        ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')
        
        # Calculate y-axis range
        all_values = []
        for key in keys:
            series = series_data[key]
            all_values.extend(series['value'].tolist())
        
        y_min = min(all_values)
        y_max = max(all_values)
        y_bottom = int(y_min) - 1 if y_min < 0 else 0
        y_top = max(8, int(y_max) + 1)
        
        ax.set_ylim(y_bottom, y_top)
        ax.set_yticks(range(y_bottom, y_top + 1))
        ax.set_yticklabels([f'{i}%' for i in range(y_bottom, y_top + 1)])
        ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        
        # Labels and title
        x_label = self.x_label_entry.get()
        y_label = self.y_label_entry.get()
        chart_title = self.title_entry.get()
        
        if x_label:
            ax.set_xlabel(x_label)
        if y_label:
            ax.set_ylabel(y_label)
        if chart_title:
            ax.set_title(chart_title)
        
        # Add labels on lines
        if len(keys) >= 1:
            ax.text(datetime(2021, 8, 1), 5.8, self.series_labels[keys[0]], 
                   fontsize=12, color=self.series_colors[keys[0]], weight='bold')
        if len(keys) >= 2:
            ax.text(datetime(2022, 6, 1), 4.5, self.series_labels[keys[1]], 
                   fontsize=12, color=self.series_colors[keys[1]], weight='bold')
        if len(keys) >= 3:
            ax.text(datetime(2023, 6, 1), 2.0, self.series_labels[keys[2]], 
                   fontsize=12, color=self.series_colors[keys[2]], weight='bold')
        
        # Add data table if enabled
        if self.show_table_var.get() and len(keys) >= 2:
            try:
                from_date = self.from_date_entry.get() + "-01"
                to_date = self.to_date_entry.get() + "-01"
                
                table_lines = []
                from_month = pd.to_datetime(from_date).strftime('%b %Y')
                to_month = pd.to_datetime(to_date).strftime('%b %Y')
                table_lines.append(f"{from_month}  {to_month}   Chg.")
                
                for key in keys:
                    series = series_data[key]
                    s_from = series[series['date'] == from_date]
                    s_to = series[series['date'] == to_date]
                    
                    if not (s_from.empty or s_to.empty):
                        s_from_val = s_from.iloc[0]['value']
                        s_to_val = s_to.iloc[0]['value']
                        change = (s_to_val - s_from_val) * 100
                        
                        label = self.series_labels[key]
                        table_lines.append(f"{label:<8} {s_from_val:.2f}%     {s_to_val:.2f}%   {change:+.0f} b.p.")
                
                if len(table_lines) > 1:
                    table_text = "\n".join(table_lines)
                    ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10, 
                            verticalalignment='bottom', horizontalalignment='right',
                            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            except:
                pass
        
        # Style
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

if __name__ == "__main__":
    root = tk.Tk()
    app = PCEChartCustomizer(root)
    root.mainloop()