import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the CSV file
df = pd.read_csv('01a-YoY-PCE.csv')
df['date'] = pd.to_datetime(df['date'])

# Create plot
fig, ax = plt.subplots(figsize=(14, 8))

# Plot Headline
series = df[df['key'] == 'YoY_pce_headline'].copy()
ax.plot(series['date'], series['value'], color='#1f77b4', linewidth=2.5, label='Headline')

# Plot Core
series = df[df['key'] == 'YoY_pce_core'].copy()
ax.plot(series['date'], series['value'], color='#7cb342', linewidth=2.5, label='Core')

# Add 2% reference line
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
