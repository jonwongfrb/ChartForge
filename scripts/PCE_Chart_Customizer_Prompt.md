Create a Python GUI application for customizable timeseries chart generation with the following specifications:

## Core Requirements

**Data Format:** CSV files with columns: `date`, `key`, `value`, `lbl`
- Multiple timeseries identified by unique `key` values
- Date column in YYYY-MM-DD format
- Value column contains numeric data

**Initial Behavior:**
- Load CSV file and display exact original chart first
- Auto-detect all timeseries from unique `key` values
- Show original styling: blue (#1f77b4) for first series, green (#7cb342) for second, orange (#ff7f0e) for third
- Include 2% reference line (dashed black)
- Add COVID recession shading (gray, Feb-Apr 2020)
- Display series labels directly on chart lines (not legend box)
- Show data table in bottom-right with last two data points and basis point changes

## GUI Features

**File Operations:**
- Load CSV File button
- Auto-detect and plot all timeseries

**Customization Controls:**
- Dynamic color buttons for each detected series
- Dynamic label entry fields for each detected series
- Legend position dropdown (none, upper/lower left/right, center)
- X-axis label, Y-axis label, Chart title fields
- Data table controls: show/hide checkbox, from/to date range (YYYY-MM format)

**Action Buttons:**
- Update Chart - Apply all customizations
- Revert to Original - Reset all settings and show original chart
- Export Python Script - Generate standalone Python script with hardcoded customizations
- Export R Script - Generate ggplot2 R script with hardcoded customizations

## Technical Specifications

**Libraries Required:**
```bash
pip install pandas matplotlib
```

**Key Features:**
- Auto-generate friendly labels from keys (e.g., "YoY_pce_headline" → "Headline")
- Dynamic y-axis scaling (handles negative values automatically)
- Line labels positioned on chart with matching colors
- Data table shows all series with customizable date range
- Basis point calculations: (new_value - old_value) * 100
- Export functions generate working standalone scripts

**Chart Styling:**
- Figure size: 14x8 for original, 10x6 for customized
- Line width: 2.5
- Grid: alpha=0.3
- Remove top/right spines
- Date range: 2019-2026
- Y-axis: Dynamic based on data range, minimum 0-8%

**GUI Layout:**
- Left panel: All controls (200px width)
- Right panel: Chart display (expandable)
- Window size: 1200x800

**Data Table Format:**
```
Oct 2025  Dec 2025   Chg.
Headline    2.678%     3.123%   +45 b.p.
Core        2.734%     2.746%   +1 b.p.
Base        0.734%     1.746%   +101 b.p.
```

**Export Capabilities:**
- Python scripts use matplotlib with all customizations hardcoded
- R scripts use ggplot2 with all customizations hardcoded
- Both include data loading, plotting, styling, and table generation

This creates a comprehensive timeseries chart customizer that works with any CSV following the specified format.