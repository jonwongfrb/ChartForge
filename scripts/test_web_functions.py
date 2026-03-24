import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Test the web app functions with actual data
def test_web_app_functions():
    # Read the CSV data
    df = pd.read_csv('../01a-YoY-PCE.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    print("Data loaded successfully!")
    print(f"Shape: {df.shape}")
    print(f"Keys: {df['key'].unique()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Test the series detection
    keys = list(df['key'].unique())
    series_data = {}
    
    for key in keys:
        series_data[key] = df[df['key'] == key].copy()
    
    print(f"Series detected: {list(series_data.keys())}")
    
    # Test chart creation (similar to web app)
    fig = go.Figure()
    
    colors = {'YoY_pce_headline': '#1f77b4', 'YoY_pce_core': '#7cb342'}
    labels = {'YoY_pce_headline': 'Headline', 'YoY_pce_core': 'Core'}
    
    for key in keys:
        series = series_data[key]
        color = colors.get(key, '#ff7f0e')
        label = labels.get(key, key.replace('_', ' ').title())
        
        fig.add_trace(go.Scatter(
            x=series['date'],
            y=series['value'],
            mode='lines',
            name=label,
            line=dict(color=color, width=2.5)
        ))
    
    # Add 2% reference line
    fig.add_hline(y=2, line_dash="dash", line_color="black", opacity=0.7)
    
    # Add COVID recession shading
    fig.add_vrect(x0="2020-02-01", x1="2020-04-01", fillcolor="gray", opacity=0.2, line_width=0)
    
    # Format the chart
    fig.update_layout(
        xaxis=dict(range=["2019-01-01", "2026-01-01"]),
        yaxis=dict(ticksuffix="%"),
        width=1000,
        height=600,
        plot_bgcolor='white'
    )
    
    print("Chart created successfully!")
    
    # Test percentage changes calculation
    from_date = "2025-10"
    to_date = "2025-11"
    
    try:
        from_dt = pd.to_datetime(f"{from_date}-01")
        to_dt = pd.to_datetime(f"{to_date}-01")
        
        table_data = []
        
        for key in keys:
            series = series_data[key]
            label = labels.get(key, key.replace('_', ' ').title())
            
            # Filter data for date range
            mask = (series['date'] >= from_dt) & (series['date'] <= to_dt)
            filtered_series = series[mask].copy()
            
            if len(filtered_series) >= 2:
                start_value = filtered_series['value'].iloc[0]
                end_value = filtered_series['value'].iloc[-1]
                bp_change = (end_value - start_value) * 100
                
                table_data.append({
                    'Series': label,
                    'Start': f"{start_value:.2f}%",
                    'End': f"{end_value:.2f}%",
                    'Change (bp)': f"{bp_change:+.0f}"
                })
        
        changes_df = pd.DataFrame(table_data)
        print("Percentage changes table:")
        print(changes_df)
        
    except Exception as e:
        print(f"Error calculating changes: {e}")
    
    return fig, changes_df

if __name__ == "__main__":
    fig, table = test_web_app_functions()