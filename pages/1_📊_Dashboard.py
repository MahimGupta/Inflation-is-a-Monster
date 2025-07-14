import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils.data_fetcher import DataFetcher
from utils.calculations import InflationCalculator
from utils.charts import ChartGenerator

st.set_page_config(page_title="Dashboard - Inflation Monster", page_icon="📊", layout="wide")

@st.cache_resource
def get_data_fetcher():
    return DataFetcher()

@st.cache_resource
def get_calculator():
    return InflationCalculator()

@st.cache_resource
def get_chart_generator():
    return ChartGenerator()

def main():
    st.title("📊 Inflation Monster Dashboard")
    st.markdown("Real-time inflation analysis and key economic indicators")
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Time range selector
    time_range = st.sidebar.selectbox(
        "Select Time Range",
        ["30 Days", "90 Days", "6 Months", "1 Year", "2 Years", "5 Years"],
        index=3
    )
    
    # Convert time range to days
    range_mapping = {
        "30 Days": 30,
        "90 Days": 90,
        "6 Months": 180,
        "1 Year": 365,
        "2 Years": 730,
        "5 Years": 1825
    }
    days = range_mapping[time_range]
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh data", value=False)
    
    if auto_refresh:
        st.sidebar.info("Data will refresh every 5 minutes")
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Initialize components
    data_fetcher = get_data_fetcher()
    calculator = get_calculator()
    chart_gen = get_chart_generator()
    
    try:
        # Fetch data
        with st.spinner("Loading dashboard data..."):
            cpi_data = data_fetcher.get_cpi_data(days=days)
            m2_data = data_fetcher.get_m2_data(days=days)
            bitcoin_data = data_fetcher.get_bitcoin_data(days=days)
        
        # Key Metrics Section
        st.header("🎯 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # CPI Metrics
        if not cpi_data.empty:
            latest_cpi = cpi_data['value'].iloc[-1]
            cpi_yoy = calculator.calculate_yoy_inflation(cpi_data)
            
            with col1:
                st.metric(
                    label="Current CPI",
                    value=f"{latest_cpi:.2f}",
                    help="Consumer Price Index - All Urban Consumers"
                )
            
            with col2:
                st.metric(
                    label="Annual Inflation Rate",
                    value=f"{cpi_yoy:.2f}%",
                    help="Year-over-year CPI change"
                )
        
        # M2 Metrics
        if not m2_data.empty:
            latest_m2 = m2_data['value'].iloc[-1]
            m2_growth = calculator.calculate_money_supply_growth(m2_data)
            
            with col3:
                st.metric(
                    label="M2 Money Supply",
                    value=f"${latest_m2:.0f}B",
                    help="M2 Money Supply in billions"
                )
            
            with col4:
                st.metric(
                    label="M2 Annual Growth",
                    value=f"{m2_growth:.2f}%",
                    help="Year-over-year M2 growth rate"
                )
        
        # Bitcoin Metrics
        if not bitcoin_data.empty:
            latest_btc = bitcoin_data['price'].iloc[-1]
            btc_volatility = bitcoin_data['price'].pct_change().std() * np.sqrt(365) * 100
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="Bitcoin Price",
                    value=f"${latest_btc:,.2f}",
                    help="Current Bitcoin price in USD"
                )
            
            with col2:
                st.metric(
                    label="Bitcoin Volatility",
                    value=f"{btc_volatility:.1f}%",
                    help="Annualized volatility"
                )
        
        # Main Charts Section
        st.header("📈 Interactive Charts")
        
        # Chart tabs
        tab1, tab2, tab3 = st.tabs(["Inflation Trends", "Money Supply", "Bitcoin vs CPI"])
        
        with tab1:
            st.subheader("CPI and Inflation Rate")
            if not cpi_data.empty:
                fig = chart_gen.create_cpi_chart(cpi_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No CPI data available for the selected time range")
        
        with tab2:
            st.subheader("M2 Money Supply Growth")
            if not m2_data.empty:
                fig = chart_gen.create_m2_chart(m2_data)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No M2 data available for the selected time range")
        
        with tab3:
            st.subheader("Bitcoin vs CPI Comparison")
            if not bitcoin_data.empty and not cpi_data.empty:
                fig = chart_gen.create_dual_axis_chart(
                    cpi_data, bitcoin_data,
                    title="CPI vs Bitcoin Price",
                    y1_title="CPI",
                    y2_title="Bitcoin Price ($)"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Insufficient data for comparison chart")
        
        # Summary Statistics
        st.header("📊 Summary Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("CPI Statistics")
            if not cpi_data.empty:
                cpi_stats = cpi_data['value'].describe()
                st.dataframe(cpi_stats, use_container_width=True)
            else:
                st.info("No CPI data available")
        
        with col2:
            st.subheader("Bitcoin Statistics")
            if not bitcoin_data.empty:
                btc_stats = bitcoin_data['price'].describe()
                st.dataframe(btc_stats, use_container_width=True)
            else:
                st.info("No Bitcoin data available")
        
        # Data freshness indicator
        st.sidebar.markdown("---")
        st.sidebar.subheader("Data Status")
        if not cpi_data.empty:
            latest_cpi_date = cpi_data.index[-1].strftime("%Y-%m-%d")
            st.sidebar.success(f"CPI: Updated {latest_cpi_date}")
        
        if not bitcoin_data.empty:
            latest_btc_date = bitcoin_data.index[-1].strftime("%Y-%m-%d")
            st.sidebar.success(f"Bitcoin: Updated {latest_btc_date}")
        
        if not m2_data.empty:
            latest_m2_date = m2_data.index[-1].strftime("%Y-%m-%d")
            st.sidebar.success(f"M2: Updated {latest_m2_date}")
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.info("Please check your internet connection and try refreshing the page.")

if __name__ == "__main__":
    main()
