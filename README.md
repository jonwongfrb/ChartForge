# Charting Assistant

A comprehensive toolkit for creating customizable economic charts and visualizations, specifically designed for PCE (Personal Consumption Expenditures) inflation data analysis.

## Overview

This project provides multiple interfaces for generating, customizing, and analyzing economic time series charts:

- **Desktop GUI Application** - Full-featured chart customizer with Tkinter
- **Web Application** - Streamlit-based interactive chart generator
- **Command Line Tools** - Python scripts for automated chart generation

## Features

### 🎨 Chart Customization
- **Dynamic Series Detection** - Automatically detects all time series from CSV data
- **Color Customization** - Individual color selection for each data series
- **Label Management** - Custom labels with intelligent defaults
- **Legend Control** - Flexible legend positioning or removal
- **Reference Lines** - 2% inflation target line with COVID recession shading
- **Dual View Modes** - Toggle between interactive charts and export preview

### 📊 Data Analysis
- **Percentage Change Tables** - Basis point calculations between date ranges
- **Analytics Summary** - Comprehensive statistical analysis
- **Narrative Generation** - Plain language data summaries
- **Comparative Analysis** - Multi-series comparison tools

### 💾 Export Capabilities
- **PNG Export** - High-quality PNG images (300 DPI)
- **PDF Export** - Publication-ready PDF documents
- **Python Scripts** - Generate standalone matplotlib code
- **R Scripts** - Export to ggplot2 format
- **Export Preview** - See exactly how your exports will look before downloading
- **Data Tables** - Formatted percentage change tables

## Project Structure

```
charting_assistant/
├── scripts/
│   ├── pce_chart_web.py          # Streamlit web application
│   ├── pce_chart_customizer.py   # Desktop GUI application
│   ├── pce_chart_generator.py    # Command line generator
│   └── PCE_Chart_Customizer_Prompt.md  # Technical specifications
├── *.csv                         # Sample PCE data files
├── *.png                         # Generated chart examples
└── README.md                     # This file
```

## Installation

### Requirements
```bash
pip install pandas matplotlib plotly streamlit
```

**Note:** `tkinter` is included with most Python installations. If not available, install it via your system package manager.

### Quick Start
1. Clone the repository
2. Install dependencies: `pip install pandas matplotlib plotly streamlit`
3. Run your preferred interface:
   - **Web App**: `streamlit run scripts/pce_chart_web.py`
   - **Desktop GUI**: `python scripts/pce_chart_customizer.py`

## Usage

### Data Format
CSV files should contain these columns:
- `date` - Date in YYYY-MM-DD format
- `key` - Unique identifier for each time series
- `value` - Numeric data values
- `lbl` - Optional labels (auto-generated if missing)

Example:
```csv
date,key,value,lbl
2023-01-01,YoY_pce_headline,2.5,Headline PCE
2023-01-01,YoY_pce_core,2.8,Core PCE
```

### Web Application (Streamlit)

The web interface provides:
- **File Upload** - Drag and drop CSV files
- **Real-time Customization** - Instant chart updates
- **Dual Chart Views** - Toggle between interactive Plotly charts and export preview
- **Analytics Dashboard** - Statistical summaries and insights
- **Export Options** - Download PNG, PDF, Python, and R scripts

Key features:
- Auto-detection of PCE data with preset styling
- Interactive color and label customization
- Basis point change calculations
- Narrative summary generation
- Export preview tab shows exactly how PNG/PDF will look

### Desktop GUI (Tkinter)

The desktop application offers:
- **Export Preview Mode** - Shows exactly how PNG/PDF exports will look (default view)
- **Customized View Mode** - Compact view with your modifications
- **Advanced Customization** - Full control over all chart elements
- **Data Table Integration** - Embedded percentage change tables
- **Multiple Export Formats** - PNG, PDF, Python, and R scripts

Workflow:
1. Load CSV file
2. Review export preview (14x8 inch chart)
3. Customize colors, labels, and styling
4. Toggle between export preview and customized view
5. Export as PNG, PDF, or script

### Command Line Tools

For automated workflows:
```bash
python scripts/pce_chart_generator.py input.csv --output chart.png
```

## Sample Data

The project includes various PCE inflation datasets:
- `01a-YoY-PCE.csv` - Year-over-year headline and core PCE
- `01b-MoM-PCE.csv` - Month-over-month PCE changes
- `02a-Headline-Annualized.csv` - Annualized headline inflation
- `3a-annualized-headlinecore.csv` - Comparative headline vs core

## Chart Features

### Automatic Styling
- **Default Colors**: Blue (#1f77b4), Green (#7cb342), Orange (#ff7f0e)
- **Reference Lines**: 2% inflation target (dashed black)
- **Recession Shading**: COVID period (Feb-Apr 2020, gray)
- **Dynamic Y-Axis**: Auto-scales based on data range

### Data Tables
Embedded tables show:
- Start and end values for selected date ranges
- Basis point changes: `(new_value - old_value) * 100`
- Multiple series comparison

### Analytics
- Statistical summaries (mean, median, std dev)
- Trend analysis (6-month, 12-month averages)
- Target comparison (above/below 2%)
- Volatility measures

## Export Formats

### PNG Images
- High-resolution output (300 DPI)
- Publication-ready quality
- Matches export preview exactly
- 14x8 inch dimensions

### PDF Documents
- Vector-based graphics
- Scalable without quality loss
- Professional formatting
- Ideal for reports and presentations

### Python Scripts
Generated scripts include:
- Complete matplotlib setup
- Data loading and processing
- All customizations hardcoded
- Styling and formatting

### R Scripts
ggplot2 exports feature:
- Data manipulation with dplyr
- Custom color scales
- Theme customization
- Annotation layers

## Technical Specifications

### Chart Dimensions
- **Export Preview/PNG/PDF**: 14x8 inches
- **Customized View**: 10x6 inches
- **Line Width**: 2.5 points
- **Date Range**: 2019-2026
- **PNG Resolution**: 300 DPI

### Performance
- Handles multiple time series efficiently
- Real-time updates in web interface
- Optimized for economic data patterns

## Use Cases

### Economic Research
- PCE inflation analysis
- Federal Reserve policy tracking
- Academic research visualization

### Financial Analysis
- Investment decision support
- Market trend identification
- Risk assessment tools

### Reporting
- Automated chart generation
- Consistent styling across reports
- Multi-format export capabilities

## Contributing

This project is designed for economic data visualization. When adding features:
1. Maintain compatibility with existing CSV format
2. Follow established styling conventions
3. Include both GUI and programmatic interfaces
4. Add appropriate documentation

## License

Open source project for economic data visualization and analysis.