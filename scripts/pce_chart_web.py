import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages

st.set_page_config(page_title="ChartForge", layout="wide")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'series_colors' not in st.session_state:
    st.session_state.series_colors = {}
if 'series_labels' not in st.session_state:
    st.session_state.series_labels = {}

default_colors = ['#1f77b4', '#7cb342', '#ff7f0e', '#d62728', '#9467bd', '#8c564b']

def detect_data_keys(df):
    return list(df['key'].unique()) if df is not None else []

def get_all_data_series(df):
    keys = detect_data_keys(df)
    series_data = {}
    
    for i, key in enumerate(keys):
        series = df[df['key'] == key].copy()
        series_data[key] = series
        
        if key not in st.session_state.series_colors:
            st.session_state.series_colors[key] = default_colors[i % len(default_colors)]
        if key not in st.session_state.series_labels:
            label = key.replace('YoY_pce_', '').replace('MoM_pce_', '').replace('_pce_', '').replace('_', ' ').title()
            st.session_state.series_labels[key] = label if label else key.replace('_', ' ').title()
    
    return series_data, keys

def generate_literal_summary(series_data, keys):
    """Generate plain language narrative summary"""
    summary = ""
    
    for key in keys:
        series = series_data[key]
        label = st.session_state.series_labels[key]
        values = series['value'].values
        
        current = values[-1]
        prev_month = values[-2]
        mom_change = (current - prev_month) * 100
        
        recent_3m = values[-3:]
        trend = "rising" if recent_3m[-1] > recent_3m[0] else "falling" if recent_3m[-1] < recent_3m[0] else "stable"
        
        max_val = values.max()
        max_date = series[series['value'] == max_val]['date'].iloc[0].strftime('%B %Y')
        
        vs_target = "above" if current > 2 else "below" if current < 2 else "at"
        
        summary += f"{label} currently stands at {current:.2f}%, {vs_target} the 2% target. "
        summary += f"The indicator has {trend} over the past three months, "
        summary += f"with a month-over-month change of {mom_change:+.0f} basis points. "
        summary += f"The peak was {max_val:.2f}% in {max_date}. "
        
        if len(values) >= 12:
            yoy_change = (current - values[-12]) * 100
            direction = "increased" if yoy_change > 0 else "decreased"
            summary += f"Year-over-year, {label} has {direction} by {abs(yoy_change):.0f} basis points.\n\n"
        else:
            summary += "\n\n"
    
    if len(keys) >= 2:
        key1, key2 = keys[0], keys[1]
        label1, label2 = st.session_state.series_labels[key1], st.session_state.series_labels[key2]
        val1 = series_data[key1]['value'].values[-1]
        val2 = series_data[key2]['value'].values[-1]
        spread = (val1 - val2) * 100
        
        higher = label1 if val1 > val2 else label2
        lower = label2 if val1 > val2 else label1
        
        summary += f"Comparing the two series, {higher} is currently running {abs(spread):.0f} basis points higher than {lower}. "
        summary += f"{label1} is at {val1:.2f}% while {label2} is at {val2:.2f}%.\n"
    
    return summary

def calculate_percentage_changes(series_data, keys, from_date, to_date, periods=[1, 3, 6, 12]):
    """Calculate basis point changes for the date range"""
    try:
        # Parse date range
        from_dt = pd.to_datetime(f"{from_date}-01")
        to_dt = pd.to_datetime(f"{to_date}-01")
        
        # Create styled table data showing only basis point changes
        table_data = []
        
        for key in keys:
            series = series_data[key]
            label = st.session_state.series_labels[key]
            
            # Filter data for date range
            mask = (series['date'] >= from_dt) & (series['date'] <= to_dt)
            filtered_series = series[mask].copy()
            
            if len(filtered_series) < 2:
                continue
                
            # Get start and end values for the range
            start_value = filtered_series['value'].iloc[0]
            end_value = filtered_series['value'].iloc[-1]
            
            # Calculate basis point change over the entire range
            bp_change = (end_value - start_value) * 100  # Convert to basis points
            
            table_data.append({
                'Series': label,
                'Start': f"{start_value:.2f}%",
                'End': f"{end_value:.2f}%",
                'Change (bp)': f"{bp_change:+.0f}"
            })
        
        return pd.DataFrame(table_data) if table_data else None
        
    except Exception as e:
        return None

def create_styled_table_html(df):
    """Create PNG-style HTML table for basis point changes"""
    if df is None or df.empty:
        return "<div style='text-align: center; color: #666;'>No data for selected range</div>"
    
    html = """
    <style>
    .pce-table {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        border-collapse: collapse;
        width: 100%;
        font-size: 12px;
        background: white;
        border: 1px solid #ddd;
    }
    .pce-table th {
        background-color: #f8f9fa;
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
        font-weight: bold;
        color: #333;
    }
    .pce-table td {
        border: 1px solid #ddd;
        padding: 6px 8px;
        text-align: center;
        color: #333;
    }
    .pce-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    .pce-table tr:hover {
        background-color: #f5f5f5;
    }
    </style>
    <table class="pce-table">
    <thead>
        <tr><th>Series</th><th>Start</th><th>End</th><th>Change (bp)</th></tr>
    </thead>
    <tbody>
    """
    
    for _, row in df.iterrows():
        html += f"<tr><td>{row['Series']}</td><td>{row['Start']}</td><td>{row['End']}</td><td>{row['Change (bp)']}</td></tr>"
    
    html += "</tbody></table>"
    return html

def generate_analytics(series_data, keys):
    summary = "DATA ANALYTICS SUMMARY\n" + "=" * 50 + "\n\n"
    
    for key in keys:
        series = series_data[key]
        label = st.session_state.series_labels[key]
        values = series['value'].values
        
        summary += f"{label.upper()}\n" + "-" * 30 + "\n"
        summary += f"Current Value: {values[-1]:.2f}%\n"
        summary += f"Mean: {values.mean():.2f}%\n"
        summary += f"Median: {pd.Series(values).median():.2f}%\n"
        summary += f"Min: {values.min():.2f}% ({series[series['value'] == values.min()]['date'].iloc[0].strftime('%b %Y')})\n"
        summary += f"Max: {values.max():.2f}% ({series[series['value'] == values.max()]['date'].iloc[0].strftime('%b %Y')})\n"
        summary += f"Std Dev: {values.std():.2f}%\n"
        
        recent_6m = values[-6:]
        recent_12m = values[-12:]
        summary += f"\n6-Month Avg: {recent_6m.mean():.2f}%\n"
        summary += f"12-Month Avg: {recent_12m.mean():.2f}%\n"
        
        mom_change = (values[-1] - values[-2]) * 100
        summary += f"\nMonth-over-Month Change: {mom_change:+.0f} b.p.\n"
        if len(values) >= 12:
            yoy_change = (values[-1] - values[-12]) * 100
            summary += f"Year-over-Year Change: {yoy_change:+.0f} b.p.\n"
        
        above_2 = (values > 2).sum()
        below_2 = (values <= 2).sum()
        summary += f"\nMonths Above 2%: {above_2} ({above_2/len(values)*100:.1f}%)\n"
        summary += f"Months At/Below 2%: {below_2} ({below_2/len(values)*100:.1f}%)\n"
        summary += "\n" + "=" * 50 + "\n\n"
    
    if len(keys) >= 2:
        summary += "COMPARATIVE ANALYSIS\n" + "=" * 50 + "\n"
        for i in range(len(keys)):
            for j in range(i+1, len(keys)):
                key1, key2 = keys[i], keys[j]
                label1, label2 = st.session_state.series_labels[key1], st.session_state.series_labels[key2]
                val1 = series_data[key1]['value'].values[-1]
                val2 = series_data[key2]['value'].values[-1]
                spread = (val1 - val2) * 100
                summary += f"\n{label1} vs {label2}:\n"
                summary += f"Current Spread: {spread:+.0f} b.p.\n"
                summary += f"{label1}: {val1:.2f}%\n"
                summary += f"{label2}: {val2:.2f}%\n"
    
    return summary

def create_matplotlib_chart(df, series_data, keys, x_label, y_label, chart_title, legend_pos, show_table, from_date, to_date, series_colors, series_labels):
    """Create matplotlib version that matches the original PNG exactly"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Plot all series
    for key in keys:
        series = series_data[key]
        color = series_colors[key]
        label = series_labels[key]
        ax.plot(series['date'], series['value'], color=color, linewidth=2.5, label=label)
    
    # Add 2% reference line
    ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)
    
    # Add COVID recession shading
    ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')
    
    # Calculate y-axis range
    all_values = [series_data[key]['value'].values for key in keys]
    all_values = [v for sublist in all_values for v in sublist]
    y_min, y_max = min(all_values), max(all_values)
    y_bottom = int(y_min) - 1 if y_min < 0 else 0
    y_top = max(8, int(y_max) + 1)
    
    ax.set_ylim(y_bottom, y_top)
    ax.set_yticks(range(y_bottom, y_top + 1))
    ax.set_yticklabels([f'{i}%' for i in range(y_bottom, y_top + 1)])
    ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    # Labels and title
    if x_label:
        ax.set_xlabel(x_label)
    if y_label:
        ax.set_ylabel(y_label)
    if chart_title:
        ax.set_title(chart_title)
    
    # Add labels on lines
    if len(keys) >= 1:
        ax.text(datetime(2021, 8, 1), 5.8, series_labels[keys[0]], 
               fontsize=12, color=series_colors[keys[0]], weight='bold')
    if len(keys) >= 2:
        ax.text(datetime(2022, 6, 1), 4.5, series_labels[keys[1]], 
               fontsize=12, color=series_colors[keys[1]], weight='bold')
    if len(keys) >= 3:
        ax.text(datetime(2023, 6, 1), 2.0, series_labels[keys[2]], 
               fontsize=12, color=series_colors[keys[2]], weight='bold')
    
    # Add data table if enabled
    if show_table and len(keys) >= 2:
        try:
            from_dt = pd.to_datetime(f"{from_date}-01")
            to_dt = pd.to_datetime(f"{to_date}-01")
            
            table_lines = []
            from_month = from_dt.strftime('%b %Y')
            to_month = to_dt.strftime('%b %Y')
            table_lines.append(f"{from_month}  {to_month}   Chg.")
            
            for key in keys:
                series = series_data[key]
                s_from = series[series['date'] == from_dt]
                s_to = series[series['date'] == to_dt]
                
                if not (s_from.empty or s_to.empty):
                    s_from_val = s_from.iloc[0]['value']
                    s_to_val = s_to.iloc[0]['value']
                    change = (s_to_val - s_from_val) * 100
                    
                    label = series_labels[key]
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

def create_chart(df, series_data, keys, x_label, y_label, chart_title, legend_pos, show_table, from_date, to_date):
    fig = go.Figure()
    
    # Auto-detect if this is PCE data and set appropriate styling
    is_pce_data = any('pce' in key.lower() for key in keys)
    
    for i, key in enumerate(keys):
        series = series_data[key]
        color = st.session_state.series_colors[key]
        label = st.session_state.series_labels[key]
        
        fig.add_trace(go.Scatter(
            x=series['date'],
            y=series['value'],
            mode='lines',
            name=label,
            line=dict(color=color, width=2.5),
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x|%b %Y}<br>Value: %{y:.2f}%<extra></extra>'
        ))
    
    # Add 2% reference line for PCE data
    if is_pce_data:
        fig.add_hline(y=2, line_dash="dash", line_color="black", opacity=0.7, 
                     annotation_text="2% Target", annotation_position="bottom right")
    
    # COVID recession shading
    fig.add_vrect(x0="2020-02-01", x1="2020-04-01", fillcolor="gray", opacity=0.2, line_width=0)
    
    # Auto-calculate Y-axis range
    all_values = [series_data[key]['value'].values for key in keys]
    all_values = [v for sublist in all_values for v in sublist]
    y_min, y_max = min(all_values), max(all_values)
    y_bottom = int(y_min) - 1 if y_min < 0 else 0
    y_top = max(8, int(y_max) + 1)
    
    # Set title based on data type
    if not chart_title and is_pce_data:
        chart_title = "PCE Inflation: Year-over-Year % Change"
    
    fig.update_layout(
        title=dict(text=chart_title, x=0.5, font=dict(size=16, color='black')) if chart_title else None,
        xaxis_title=x_label if x_label else None,
        yaxis_title=y_label if y_label else "Percent",
        xaxis=dict(
            range=["2019-01-01", "2026-01-01"],
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        yaxis=dict(
            range=[y_bottom, y_top], 
            ticksuffix="%",
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=0.5
        ),
        showlegend=(legend_pos != 'none'),
        legend=dict(
            x=0.02, y=0.98,
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='gray',
            borderwidth=1
        ) if legend_pos == 'upper left' else
              dict(x=0.98, y=0.98, xanchor='right', bgcolor='rgba(255,255,255,0.8)', bordercolor='gray', borderwidth=1) if legend_pos == 'upper right' else
              dict(x=0.02, y=0.02, yanchor='bottom', bgcolor='rgba(255,255,255,0.8)', bordercolor='gray', borderwidth=1) if legend_pos == 'lower left' else
              dict(x=0.98, y=0.02, xanchor='right', yanchor='bottom', bgcolor='rgba(255,255,255,0.8)', bordercolor='gray', borderwidth=1) if legend_pos == 'lower right' else
              dict(x=0.5, y=0.5, bgcolor='rgba(255,255,255,0.8)', bordercolor='gray', borderwidth=1),
        hovermode='x unified',
        width=1000,
        height=600,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

# Main UI
st.title("ChartForge")

col1, col2 = st.columns([1, 3])

with col1:
    st.header("Controls")
    
    uploaded_file = st.file_uploader("Upload CSV File", type=['csv'])
    if uploaded_file:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.session_state.df['date'] = pd.to_datetime(st.session_state.df['date'])
        
        # Auto-configure for PCE data
        if '01a-YoY-PCE.csv' in uploaded_file.name or 'pce' in uploaded_file.name.lower():
            # Set default colors for PCE data
            keys = detect_data_keys(st.session_state.df)
            if 'YoY_pce_headline' in keys:
                st.session_state.series_colors['YoY_pce_headline'] = '#1f77b4'  # Blue
                st.session_state.series_labels['YoY_pce_headline'] = 'Headline'
            if 'YoY_pce_core' in keys:
                st.session_state.series_colors['YoY_pce_core'] = '#7cb342'  # Green
                st.session_state.series_labels['YoY_pce_core'] = 'Core'
            
            # Auto-generate chart
            st.session_state.show_chart = True
        
        st.success("File loaded!")
    
    if st.session_state.df is not None:
        series_data, keys = get_all_data_series(st.session_state.df)
        
        st.subheader("Series Labels & Colors")
        for key in keys:
            label = st.text_input(f"{st.session_state.series_labels[key]} Label:", 
                                 value=st.session_state.series_labels[key], key=f"label_{key}")
            st.session_state.series_labels[key] = label
            
            color = st.color_picker(f"{label} Color:", 
                                   value=st.session_state.series_colors[key], key=f"color_{key}")
            st.session_state.series_colors[key] = color
        
        st.subheader("Chart Options")
        legend_pos = st.selectbox("Legend Position:", 
                                 ['none', 'upper left', 'upper right', 'lower left', 'lower right', 'center'])
        x_label = st.text_input("X-axis Label:")
        y_label = st.text_input("Y-axis Label:")
        chart_title = st.text_input("Chart Title:")
        
        st.subheader("Data Table")
        show_table = st.checkbox("Show Data Table", value=True)
        from_date = st.text_input("From Date (YYYY-MM):", value="2025-10")
        to_date = st.text_input("To Date (YYYY-MM):", value="2025-11")
        
        if st.button("📈 Generate Chart"):
            st.session_state.show_chart = True
        
        if st.button("📊 Generate Analytics"):
            st.session_state.show_analytics = True
        
        if st.button("📝 Generate Summary"):
            st.session_state.show_summary = True
        
        st.subheader("Export")
        col_png, col_pdf = st.columns(2)
        with col_png:
            if st.button("🖼️ Export PNG"):
                st.session_state.export_png = True
        with col_pdf:
            if st.button("📄 Export PDF"):
                st.session_state.export_pdf = True
        
        col_py, col_r = st.columns(2)
        with col_py:
            if st.button("🐍 Export Python"):
                st.session_state.export_python = True
        with col_r:
            if st.button("📊 Export R"):
                st.session_state.export_r = True

with col2:
    st.header("Chart Display")
    
    if st.session_state.df is not None and 'show_chart' in st.session_state:
        series_data, keys = get_all_data_series(st.session_state.df)
        
        # Create tabs for different chart views
        tab1, tab2 = st.tabs(["📊 Interactive Chart", "🖼️ Export Preview (PNG/PDF)"])
        
        with tab1:
            fig = create_chart(st.session_state.df, series_data, keys, x_label, y_label, 
                              chart_title, legend_pos, show_table, from_date, to_date)
            
            # Display chart and percentage changes side by side
            col_chart, col_table = st.columns([3, 1])
            
            with col_chart:
                st.plotly_chart(fig, use_container_width=True)
            
            with col_table:
                # Calculate and display percentage changes for date range
                changes_df = calculate_percentage_changes(series_data, keys, from_date, to_date)
                if changes_df is not None and not changes_df.empty:
                    st.markdown("#### 📊 Data Table")
                    table_html = create_styled_table_html(changes_df)
                    st.markdown(table_html, unsafe_allow_html=True)
                else:
                    st.markdown("#### 📊 Data Table")
                    st.info("No data for selected range")
        
        with tab2:
            # Create and display matplotlib chart (matches PNG/PDF export)
            fig_mpl = create_matplotlib_chart(st.session_state.df, series_data, keys, x_label, y_label, 
                                             chart_title, legend_pos, show_table, from_date, to_date,
                                             st.session_state.series_colors, st.session_state.series_labels)
            st.pyplot(fig_mpl)
            st.info("👆 This is exactly how your PNG/PDF export will look")
            plt.close(fig_mpl)
    
    if st.session_state.df is not None and 'show_analytics' in st.session_state:
        series_data, keys = get_all_data_series(st.session_state.df)
        analytics = generate_analytics(series_data, keys)
        st.text_area("Analytics Summary", analytics, height=400)
    
    if st.session_state.df is not None and 'show_summary' in st.session_state:
        series_data, keys = get_all_data_series(st.session_state.df)
        narrative = generate_literal_summary(series_data, keys)
        st.subheader("📝 Narrative Summary")
        st.write(narrative)
    
    if st.session_state.df is not None and 'export_python' in st.session_state:
        series_data, keys = get_all_data_series(st.session_state.df)
        
        script = f'''import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

df = pd.read_csv('your_data_file.csv')
df['date'] = pd.to_datetime(df['date'])

fig, ax = plt.subplots(figsize=(14, 8))

'''
        for key in keys:
            color = st.session_state.series_colors[key]
            label = st.session_state.series_labels[key]
            script += f"series = df[df['key'] == '{key}'].copy()\n"
            script += f"ax.plot(series['date'], series['value'], color='{color}', linewidth=2.5, label='{label}')\n\n"
        
        script += f'''ax.axhline(y=2, color='black', linestyle='--', linewidth=1, alpha=0.7)
ax.axvspan(datetime(2020, 2, 1), datetime(2020, 4, 1), alpha=0.3, color='gray')

ax.set_xlim(datetime(2019, 1, 1), datetime(2026, 1, 1))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
'''
        if x_label:
            script += f"ax.set_xlabel('{x_label}')\n"
        if y_label:
            script += f"ax.set_ylabel('{y_label}')\n"
        if chart_title:
            script += f"ax.set_title('{chart_title}')\n"
        if legend_pos != 'none':
            script += f"ax.legend(loc='{legend_pos}')\n"
        
        script += "\nax.spines['top'].set_visible(False)\nax.spines['right'].set_visible(False)\nax.grid(True, alpha=0.3)\nplt.tight_layout()\nplt.show()\n"
        
        st.download_button("💾 Download Python Script", script, "chart.py", "text/plain")
    
    if st.session_state.df is not None and 'export_r' in st.session_state:
        series_data, keys = get_all_data_series(st.session_state.df)
        
        script = '''library(ggplot2)
library(dplyr)
library(lubridate)

df <- read.csv('your_data_file.csv')
df$date <- as.Date(df$date)

p <- ggplot()
'''
        colors_r = []
        for key in keys:
            color = st.session_state.series_colors[key]
            label = st.session_state.series_labels[key]
            script += f"p <- p + geom_line(data = df[df$key == '{key}', ], aes(x = date, y = value, color = '{label}'), size = 1.2)\n"
            colors_r.append(f"'{label}' = '{color}'")
        
        script += f"\np <- p + scale_color_manual(values = c({', '.join(colors_r)}))\n"
        script += "p <- p + geom_hline(yintercept = 2, linetype = 'dashed', color = 'black')\n"
        script += "p <- p + annotate('rect', xmin = as.Date('2020-02-01'), xmax = as.Date('2020-04-01'), ymin = -Inf, ymax = Inf, alpha = 0.3, fill = 'gray')\n"
        
        if x_label:
            script += f"p <- p + xlab('{x_label}')\n"
        if y_label:
            script += f"p <- p + ylab('{y_label}')\n"
        if chart_title:
            script += f"p <- p + ggtitle('{chart_title}')\n"
        if legend_pos == 'none':
            script += "p <- p + theme(legend.position = 'none')\n"
        
        script += "\np <- p + theme_minimal()\nprint(p)\n"
        
        st.download_button("💾 Download R Script", script, "chart.R", "text/plain")
    
    if st.session_state.df is not None and 'export_png' in st.session_state:
        series_data, keys = get_all_data_series(st.session_state.df)
        fig_mpl = create_matplotlib_chart(st.session_state.df, series_data, keys, x_label, y_label, 
                                         chart_title, legend_pos, show_table, from_date, to_date,
                                         st.session_state.series_colors, st.session_state.series_labels)
        
        # Save to PNG
        buf = io.BytesIO()
        fig_mpl.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig_mpl)
        
        st.download_button("💾 Download PNG", buf, "chart.png", "image/png")
    
    if st.session_state.df is not None and 'export_pdf' in st.session_state:
        series_data, keys = get_all_data_series(st.session_state.df)
        fig_mpl = create_matplotlib_chart(st.session_state.df, series_data, keys, x_label, y_label, 
                                         chart_title, legend_pos, show_table, from_date, to_date,
                                         st.session_state.series_colors, st.session_state.series_labels)
        
        # Save to PDF
        buf = io.BytesIO()
        with PdfPages(buf) as pdf:
            pdf.savefig(fig_mpl, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig_mpl)
        
        st.download_button("💾 Download PDF", buf, "chart.pdf", "application/pdf")
