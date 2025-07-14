import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils.data_fetcher import DataFetcher
from utils.calculations import InflationCalculator
from utils.charts import ChartGenerator

st.set_page_config(page_title="Historical Analysis - Inflation Monster", page_icon="📈", layout="wide")

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
    st.title("📈 Historical Analysis")
    st.markdown("Deep dive into long-term inflation trends and economic patterns")
    
    # Sidebar controls
    st.sidebar.header("Analysis Controls")
    
    # Date range selector
    analysis_period = st.sidebar.selectbox(
        "Analysis Period",
        ["1 Year", "2 Years", "5 Years", "10 Years", "All Available Data"],
        index=2
    )
    
    # Analysis type
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Trend Analysis", "Volatility Analysis", "Seasonal Patterns", "Comparative Analysis"],
        index=0
    )
    
    # Convert period to days
    period_mapping = {
        "1 Year": 365,
        "2 Years": 730,
        "5 Years": 1825,
        "10 Years": 3650,
        "All Available Data": None
    }
    days = period_mapping[analysis_period]
    
    # Initialize components
    data_fetcher = get_data_fetcher()
    calculator = get_calculator()
    chart_gen = get_chart_generator()
    
    try:
        # Fetch historical data
        with st.spinner("Loading historical data..."):
            cpi_data = data_fetcher.get_cpi_data(days=days)
            m2_data = data_fetcher.get_m2_data(days=days)
            bitcoin_data = data_fetcher.get_bitcoin_data(days=days)
        
        # Trend Analysis
        if analysis_type == "Trend Analysis":
            st.header("📊 Long-term Trend Analysis")
            
            # CPI Trend
            if not cpi_data.empty:
                st.subheader("CPI Historical Trend")
                
                # Calculate moving averages
                cpi_data['MA_30'] = cpi_data['value'].rolling(window=30).mean()
                cpi_data['MA_90'] = cpi_data['value'].rolling(window=90).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=cpi_data.index,
                    y=cpi_data['value'],
                    mode='lines',
                    name='CPI',
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=cpi_data.index,
                    y=cpi_data['MA_30'],
                    mode='lines',
                    name='30-Day MA',
                    line=dict(color='red', dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=cpi_data.index,
                    y=cpi_data['MA_90'],
                    mode='lines',
                    name='90-Day MA',
                    line=dict(color='green', dash='dash')
                ))
                
                fig.update_layout(
                    title="CPI with Moving Averages",
                    xaxis_title="Date",
                    yaxis_title="CPI Value",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate trend statistics
                cpi_trend = calculator.calculate_trend_statistics(cpi_data['value'])
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Annual Growth", f"{cpi_trend['annual_growth']:.2f}%")
                with col2:
                    st.metric("Volatility", f"{cpi_trend['volatility']:.2f}%")
                with col3:
                    st.metric("Trend Direction", cpi_trend['trend_direction'])
            
            # Bitcoin Trend
            if not bitcoin_data.empty:
                st.subheader("Bitcoin Historical Trend")
                
                # Calculate moving averages
                bitcoin_data['MA_30'] = bitcoin_data['price'].rolling(window=30).mean()
                bitcoin_data['MA_90'] = bitcoin_data['price'].rolling(window=90).mean()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=bitcoin_data.index,
                    y=bitcoin_data['price'],
                    mode='lines',
                    name='Bitcoin Price',
                    line=dict(color='orange')
                ))
                fig.add_trace(go.Scatter(
                    x=bitcoin_data.index,
                    y=bitcoin_data['MA_30'],
                    mode='lines',
                    name='30-Day MA',
                    line=dict(color='red', dash='dash')
                ))
                fig.add_trace(go.Scatter(
                    x=bitcoin_data.index,
                    y=bitcoin_data['MA_90'],
                    mode='lines',
                    name='90-Day MA',
                    line=dict(color='green', dash='dash')
                ))
                
                fig.update_layout(
                    title="Bitcoin Price with Moving Averages",
                    xaxis_title="Date",
                    yaxis_title="Price ($)",
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Volatility Analysis
        elif analysis_type == "Volatility Analysis":
            st.header("📊 Volatility Analysis")
            
            # Calculate rolling volatility
            if not cpi_data.empty and not bitcoin_data.empty:
                cpi_vol = cpi_data['value'].pct_change().rolling(window=30).std() * np.sqrt(365) * 100
                btc_vol = bitcoin_data['price'].pct_change().rolling(window=30).std() * np.sqrt(365) * 100
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=cpi_data.index,
                    y=cpi_vol,
                    mode='lines',
                    name='CPI Volatility',
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=bitcoin_data.index,
                    y=btc_vol,
                    mode='lines',
                    name='Bitcoin Volatility',
                    line=dict(color='orange'),
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    title="30-Day Rolling Volatility Comparison",
                    xaxis_title="Date",
                    yaxis_title="CPI Volatility (%)",
                    yaxis2=dict(title="Bitcoin Volatility (%)", overlaying='y', side='right'),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Volatility statistics
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("CPI Volatility Stats")
                    st.metric("Average Volatility", f"{cpi_vol.mean():.2f}%")
                    st.metric("Max Volatility", f"{cpi_vol.max():.2f}%")
                
                with col2:
                    st.subheader("Bitcoin Volatility Stats")
                    st.metric("Average Volatility", f"{btc_vol.mean():.2f}%")
                    st.metric("Max Volatility", f"{btc_vol.max():.2f}%")
        
        # Seasonal Patterns
        elif analysis_type == "Seasonal Patterns":
            st.header("📊 Seasonal Pattern Analysis")
            
            if not cpi_data.empty:
                # Monthly patterns
                cpi_monthly = cpi_data.groupby(cpi_data.index.month)['value'].mean()
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                    y=cpi_monthly.values,
                    name='Average CPI by Month',
                    marker_color='blue'
                ))
                
                fig.update_layout(
                    title="Seasonal CPI Patterns",
                    xaxis_title="Month",
                    yaxis_title="Average CPI",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Quarterly patterns
                cpi_quarterly = cpi_data.groupby(cpi_data.index.quarter)['value'].mean()
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=['Q1', 'Q2', 'Q3', 'Q4'],
                    y=cpi_quarterly.values,
                    name='Average CPI by Quarter',
                    marker_color='green'
                ))
                
                fig.update_layout(
                    title="Quarterly CPI Patterns",
                    xaxis_title="Quarter",
                    yaxis_title="Average CPI",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Comparative Analysis
        elif analysis_type == "Comparative Analysis":
            st.header("📊 Comparative Analysis")
            
            # Year-over-year comparison
            if not cpi_data.empty and not bitcoin_data.empty:
                # Calculate YoY changes
                cpi_yoy = cpi_data['value'].pct_change(periods=365) * 100
                btc_yoy = bitcoin_data['price'].pct_change(periods=365) * 100
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=cpi_data.index,
                    y=cpi_yoy,
                    mode='lines',
                    name='CPI YoY Change',
                    line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=bitcoin_data.index,
                    y=btc_yoy,
                    mode='lines',
                    name='Bitcoin YoY Change',
                    line=dict(color='orange'),
                    yaxis='y2'
                ))
                
                fig.update_layout(
                    title="Year-over-Year Changes Comparison",
                    xaxis_title="Date",
                    yaxis_title="CPI YoY Change (%)",
                    yaxis2=dict(title="Bitcoin YoY Change (%)", overlaying='y', side='right'),
                    height=500
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("CPI Performance")
                    st.metric("Average YoY Change", f"{cpi_yoy.mean():.2f}%")
                    st.metric("Best Year", f"{cpi_yoy.max():.2f}%")
                    st.metric("Worst Year", f"{cpi_yoy.min():.2f}%")
                
                with col2:
                    st.subheader("Bitcoin Performance")
                    st.metric("Average YoY Change", f"{btc_yoy.mean():.2f}%")
                    st.metric("Best Year", f"{btc_yoy.max():.2f}%")
                    st.metric("Worst Year", f"{btc_yoy.min():.2f}%")
        
        # Data summary
        st.sidebar.markdown("---")
        st.sidebar.subheader("Data Summary")
        if not cpi_data.empty:
            st.sidebar.info(f"CPI Records: {len(cpi_data)}")
        if not bitcoin_data.empty:
            st.sidebar.info(f"Bitcoin Records: {len(bitcoin_data)}")
        if not m2_data.empty:
            st.sidebar.info(f"M2 Records: {len(m2_data)}")
        
    except Exception as e:
        st.error(f"Error in historical analysis: {str(e)}")
        st.info("Please check your data sources and try again.")

if __name__ == "__main__":
    main()
