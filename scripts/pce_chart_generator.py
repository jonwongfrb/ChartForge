import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Read the CSV file
df = pd.read_csv('01a-YoY-PCE.csv')

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])

# Separate headline and core data
headline = df[df['key'] == 'YoY_pce_headline'].copy()
core = df[df['key'] == 'YoY_pce_core'].copy()

# Create the plot
fig, ax = plt.subplots(figsize=(14, 8))

# Plot the lines
ax.plot(headline['date'], headline['value'], color='#1f77b4', linewidth=2.5, label='Headline')
ax.plot(core['date'], core['value'], color='#7cb342', linewidth=2.5, label='Core')

# Add 2% reference line
ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)

# Add COVID recession shading (March 2020)
ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')

# Set y-axis formatting
ax.set_ylim(0, 8)
ax.set_yticks(range(0, 9))
ax.set_yticklabels([f'{i}%' for i in range(0, 9)])

# Set x-axis formatting
ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

# Add labels on the lines
ax.text(datetime(2021, 8, 1), 5.8, 'Headline', fontsize=12, color='#1f77b4', weight='bold')
ax.text(datetime(2022, 6, 1), 4.5, 'Core', fontsize=12, color='#7cb342', weight='bold')

# Add data table in bottom right
latest_headline = headline.iloc[-1]['value']
latest_core = core.iloc[-1]['value']
prev_headline = headline.iloc[-2]['value']
prev_core = core.iloc[-2]['value']

table_text = f"""Oct 2025  Nov 2025   Chg.
Headline    {prev_headline:.2f}%     {latest_headline:.2f}%   {(latest_headline - prev_headline)*100:.0f} b.p.
Core        {prev_core:.2f}%     {latest_core:.2f}%   {(latest_core - prev_core)*100:.0f} b.p."""

ax.text(0.98, 0.02, table_text, transform=ax.transAxes, fontsize=10, 
        verticalalignment='bottom', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Set grid
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()