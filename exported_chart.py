import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the CSV file (update path as needed)
df = pd.read_csv('your_data_file.csv')
df['date'] = pd.to_datetime(df['date'])

# Create plot
fig, ax = plt.subplots(figsize=(14, 8))

# Plot Headline\nseries = df[df['key'] == 'YoY_pce_headline'].copy()\nax.plot(series['date'], series['value'], color='#1f77b4', linewidth=2.5, label='Headline')\n\n# Plot Core\nseries = df[df['key'] == 'YoY_pce_core'].copy()\nax.plot(series['date'], series['value'], color='#7cb342', linewidth=2.5, label='Core')\n\n# Add 2% reference line
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

ax.text(datetime(2021, 8, 1), 5.8, 'Headline', fontsize=12, color='#1f77b4', weight='bold')\nax.text(datetime(2022, 6, 1), 4.5, 'Core', fontsize=12, color='#7cb342', weight='bold')\n
# Add data table
try:
    from_dt = pd.to_datetime("2025-10-01")
    to_dt = pd.to_datetime("2025-11-01")
    
    table_lines = ["2025-10  2025-11   Chg."]
    
    series = df[df['key'] == 'YoY_pce_headline']
    from_val = series[series['date'] <= from_dt].tail(1)['value'].iloc[0]
    to_val = series[series['date'] <= to_dt].tail(1)['value'].iloc[0]
    change = (to_val - from_val) * 100
    table_lines.append(f"Headline {from_val:.3f}%     {to_val:.3f}%   {change:+.0f} b.p.")
    
    series = df[df['key'] == 'YoY_pce_core']
    from_val = series[series['date'] <= from_dt].tail(1)['value'].iloc[0]
    to_val = series[series['date'] <= to_dt].tail(1)['value'].iloc[0]
    change = (to_val - from_val) * 100
    table_lines.append(f"Core     {from_val:.3f}%     {to_val:.3f}%   {change:+.0f} b.p.")
    
    table_text = "\\n".join(table_lines)
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
plt.show()
