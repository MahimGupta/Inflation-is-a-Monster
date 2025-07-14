import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from utils.data_fetcher import DataFetcher
from utils.calculations import InflationCalculator
from utils.charts import ChartGenerator

# Configure the page
st.set_page_config(
    page_title="Inflation Monster",
    page_icon="🦹‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data fetcher
@st.cache_resource
def get_data_fetcher():
    return DataFetcher()

# Initialize calculator
@st.cache_resource
def get_calculator():
    return InflationCalculator()

# Initialize chart generator
@st.cache_resource
def get_chart_generator():
    return ChartGenerator()

def main():
    # Title and description
    st.title("🦹‍♂️ Inflation Monster")
    st.markdown("""
    ### Your Ultimate Inflation Analysis Tool
    
    Welcome to the Inflation Monster - a comprehensive tool for analyzing US inflation trends using real-time data from:
    - **Consumer Price Index (CPI)** - Federal Reserve Economic Data
    - **M2 Money Supply** - Federal Reserve Economic Data  
    - **Bitcoin Prices** - CoinGecko API
    
    Navigate through the sidebar to explore different analysis tools and visualizations.
    """)
    
    # Sidebar navigation info
    st.sidebar.title("🦹‍♂️ Inflation Monster")
    st.sidebar.markdown("""
    ### Navigation
    Use the pages above to explore:
    - 📊 **Dashboard** - Key metrics and overview
    - 📈 **Historical Analysis** - Long-term trends
    - 🔗 **Correlation Analysis** - Relationship between indicators
    - 🧮 **Inflation Calculator** - Calculate purchasing power
    - 📋 **Data Export** - Download data for further analysis
    """)
    
    # Initialize data fetcher
    data_fetcher = get_data_fetcher()
    
    # Quick overview section
    st.header("📊 Quick Overview")
    
    try:
        # Fetch latest data
        with st.spinner("Fetching latest data..."):
            cpi_data = data_fetcher.get_cpi_data(days=30)
            m2_data = data_fetcher.get_m2_data(days=30)
            bitcoin_data = data_fetcher.get_bitcoin_data(days=30)
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        
        if not cpi_data.empty:
            latest_cpi = cpi_data['value'].iloc[-1]
            previous_cpi = cpi_data['value'].iloc[-2] if len(cpi_data) > 1 else latest_cpi
            cpi_change = ((latest_cpi - previous_cpi) / previous_cpi) * 100
            
            with col1:
                st.metric(
                    label="Latest CPI",
                    value=f"{latest_cpi:.2f}",
                    delta=f"{cpi_change:.2f}%"
                )
        
        if not m2_data.empty:
            latest_m2 = m2_data['value'].iloc[-1]
            previous_m2 = m2_data['value'].iloc[-2] if len(m2_data) > 1 else latest_m2
            m2_change = ((latest_m2 - previous_m2) / previous_m2) * 100
            
            with col2:
                st.metric(
                    label="Latest M2 Money Supply (Billions)",
                    value=f"${latest_m2:.0f}B",
                    delta=f"{m2_change:.2f}%"
                )
        
        if not bitcoin_data.empty:
            latest_btc = bitcoin_data['price'].iloc[-1]
            previous_btc = bitcoin_data['price'].iloc[-2] if len(bitcoin_data) > 1 else latest_btc
            btc_change = ((latest_btc - previous_btc) / previous_btc) * 100
            
            with col3:
                st.metric(
                    label="Bitcoin Price",
                    value=f"${latest_btc:,.2f}",
                    delta=f"{btc_change:.2f}%"
                )
        
        # Quick chart
        st.subheader("30-Day Trends")
        chart_gen = get_chart_generator()
        
        if not cpi_data.empty and not bitcoin_data.empty:
            fig = chart_gen.create_dual_axis_chart(
                cpi_data, bitcoin_data,
                title="CPI vs Bitcoin Price (Last 30 Days)",
                y1_title="CPI",
                y2_title="Bitcoin Price ($)"
            )
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        st.info("Please check your internet connection and API credentials.")
    
    # Information section
    st.header("📚 About the Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data Sources")
        st.markdown("""
        - **CPI Data**: Federal Reserve Economic Data (FRED)
        - **M2 Money Supply**: Federal Reserve Economic Data (FRED)
        - **Bitcoin Prices**: CoinGecko API
        """)
    
    with col2:
        st.subheader("Key Indicators")
        st.markdown("""
        - **CPI**: Consumer Price Index measures inflation
        - **M2**: Money supply indicator
        - **Bitcoin**: Digital asset often seen as inflation hedge
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("**Inflation Monster** - Built with Streamlit | Data updated in real-time")

if __name__ == "__main__":
    main()
