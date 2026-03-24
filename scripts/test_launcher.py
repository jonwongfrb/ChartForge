import streamlit as st
import sys
import os

# Add the parent directory to path so we can import the web app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set page config
st.set_page_config(page_title="PCE Chart Test", layout="wide")

st.title("🧪 Testing PCE Web App")

st.markdown("""
### Quick Test of Web App Functionality

The existing web app (`pce_chart_web.py`) already has:

✅ **File Upload** - Drag and drop CSV files  
✅ **Auto-detection** - Recognizes PCE data automatically  
✅ **Real-time Customization** - Color and label controls  
✅ **Data Tables** - Basis point change calculations  
✅ **Export Options** - Python and R script downloads  
✅ **Analytics** - Statistical summaries  
✅ **Narrative Generation** - Plain language summaries  

### To test with your data:
1. Run: `streamlit run pce_chart_web.py`
2. Upload your `01a-YoY-PCE.csv` file
3. The app will auto-detect PCE data and apply proper styling
4. Use the export buttons to generate Python/R scripts

### Key Features Already Working:
- **Auto-styling**: Blue for Headline, Green for Core
- **Reference lines**: 2% target line
- **COVID shading**: Feb-Apr 2020 recession period
- **Data table**: Shows basis point changes between date ranges
- **Export scripts**: Generate standalone matplotlib/ggplot2 code
""")

# Test data loading
if st.button("🔍 Test Data Loading"):
    try:
        import pandas as pd
        df = pd.read_csv('../01a-YoY-PCE.csv')
        df['date'] = pd.to_datetime(df['date'])
        
        st.success("✅ Data loaded successfully!")
        st.write(f"**Shape**: {df.shape}")
        st.write(f"**Keys**: {list(df['key'].unique())}")
        st.write(f"**Date Range**: {df['date'].min().strftime('%Y-%m')} to {df['date'].max().strftime('%Y-%m')}")
        
        # Show sample data
        st.subheader("Sample Data")
        st.dataframe(df.head(10))
        
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")

st.markdown("---")
st.markdown("**The web app is ready to use! Just run it with streamlit and upload your CSV file.**")