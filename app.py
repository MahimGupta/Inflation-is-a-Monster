import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from fredapi import Fred
import os
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Inflation Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize FRED API
@st.cache_resource
def init_fred():
    fred_key = os.getenv('FRED_API_KEY', '928bfef823af054db951f38d94f04afe')
    return Fred(api_key=fred_key)

# Data fetching functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_cpi_data(days=365):
    """Get CPI data from FRED"""
    try:
        fred = init_fred()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        cpi_data = fred.get_series('CPIAUCSL', start=start_date, end=end_date)
        return cpi_data.dropna()
    except Exception as e:
        st.error(f"Error fetching CPI data: {str(e)}")
        return pd.Series()

@st.cache_data(ttl=300)
def get_m2_data(days=365):
    """Get M2 money supply data from FRED"""
    try:
        fred = init_fred()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        m2_data = fred.get_series('M2SL', start=start_date, end=end_date)
        return m2_data.dropna()
    except Exception as e:
        st.error(f"Error fetching M2 data: {str(e)}")
        return pd.Series()

@st.cache_data(ttl=300)
def get_fed_rate_data(days=365):
    """Get Federal Funds Rate data from FRED"""
    try:
        fred = init_fred()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        fed_data = fred.get_series('FEDFUNDS', start=start_date, end=end_date)
        return fed_data.dropna()
    except Exception as e:
        st.error(f"Error fetching Fed Rate data: {str(e)}")
        return pd.Series()

# Calculation functions
def calculate_inflation_rate(cpi_data, periods=12):
    """Calculate year-over-year inflation rate"""
    if len(cpi_data) < periods:
        return pd.Series()
    
    inflation_rate = ((cpi_data / cpi_data.shift(periods)) - 1) * 100
    return inflation_rate.dropna()

def calculate_m2_growth(m2_data, periods=12):
    """Calculate M2 growth rate"""
    if len(m2_data) < periods:
        return pd.Series()
    
    growth_rate = ((m2_data / m2_data.shift(periods)) - 1) * 100
    return growth_rate.dropna()

def calculate_purchasing_power(cpi_start, cpi_end, amount=100):
    """Calculate purchasing power change"""
    if cpi_start == 0 or pd.isna(cpi_start) or pd.isna(cpi_end):
        return None
    return amount * (cpi_start / cpi_end)

# Chart functions
def create_inflation_chart(cpi_data, inflation_rate):
    """Create dual-axis chart for CPI and inflation rate"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('Consumer Price Index (CPI)', 'Year-over-Year Inflation Rate (%)'),
        vertical_spacing=0.1
    )
    
    # CPI chart
    fig.add_trace(
        go.Scatter(
            x=cpi_data.index,
            y=cpi_data.values,
            mode='lines',
            name='CPI',
            line=dict(color='blue', width=2)
        ),
        row=1, col=1
    )
    
    # Inflation rate chart
    if not inflation_rate.empty:
        fig.add_trace(
            go.Scatter(
                x=inflation_rate.index,
                y=inflation_rate.values,
                mode='lines',
                name='Inflation Rate (%)',
                line=dict(color='red', width=2)
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        height=600,
        title_text="US Inflation Analysis",
        showlegend=True
    )
    
    return fig

def create_m2_chart(m2_data, m2_growth):
    """Create M2 money supply chart"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('M2 Money Supply (Billions)', 'M2 Growth Rate (%)'),
        vertical_spacing=0.1
    )
    
    # M2 supply chart
    fig.add_trace(
        go.Scatter(
            x=m2_data.index,
            y=m2_data.values,
            mode='lines',
            name='M2 Supply',
            line=dict(color='green', width=2)
        ),
        row=1, col=1
    )
    
    # M2 growth rate chart
    if not m2_growth.empty:
        fig.add_trace(
            go.Scatter(
                x=m2_growth.index,
                y=m2_growth.values,
                mode='lines',
                name='M2 Growth (%)',
                line=dict(color='orange', width=2)
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        height=600,
        title_text="US Money Supply Analysis",
        showlegend=True
    )
    
    return fig

def create_fed_rate_chart(fed_data):
    """Create Federal Funds Rate chart"""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=fed_data.index,
            y=fed_data.values,
            mode='lines',
            name='Fed Funds Rate',
            line=dict(color='purple', width=2)
        )
    )
    
    fig.update_layout(
        title="Federal Funds Rate",
        xaxis_title="Date",
        yaxis_title="Rate (%)",
        height=400
    )
    
    return fig

def create_correlation_chart(inflation_rate, m2_growth, fed_data):
    """Create correlation analysis chart"""
    # Align data by date
    common_dates = inflation_rate.index.intersection(m2_growth.index).intersection(fed_data.index)
    
    if len(common_dates) < 10:
        return None
    
    aligned_inflation = inflation_rate.loc[common_dates]
    aligned_m2 = m2_growth.loc[common_dates]
    aligned_fed = fed_data.loc[common_dates]
    
    fig = go.Figure()
    
    # Inflation vs M2 Growth
    fig.add_trace(
        go.Scatter(
            x=aligned_m2.values,
            y=aligned_inflation.values,
            mode='markers',
            name='Inflation vs M2 Growth',
            marker=dict(color='red', size=6)
        )
    )
    
    fig.update_layout(
        title="Inflation Rate vs M2 Growth Rate",
        xaxis_title="M2 Growth Rate (%)",
        yaxis_title="Inflation Rate (%)",
        height=400
    )
    
    return fig

# Main app
def main():
    st.title("📈 Inflation Tracker")
    st.markdown("*Simple, fast tracking of US inflation using CPI, M2, and Fed data*")
    
    # Sidebar controls
    st.sidebar.header("Settings")
    time_period = st.sidebar.selectbox(
        "Time Period",
        ["1 Year", "2 Years", "5 Years", "10 Years"],
        index=0
    )
    
    days_map = {"1 Year": 365, "2 Years": 730, "5 Years": 1825, "10 Years": 3650}
    days = days_map[time_period]
    
    # Data fetching
    with st.spinner("Loading data..."):
        cpi_data = get_cpi_data(days)
        m2_data = get_m2_data(days)
        fed_data = get_fed_rate_data(days)
    
    if cpi_data.empty or m2_data.empty or fed_data.empty:
        st.error("Unable to fetch data. Please check your internet connection and try again.")
        return
    
    # Calculate metrics
    inflation_rate = calculate_inflation_rate(cpi_data)
    m2_growth = calculate_m2_growth(m2_data)
    
    # Key metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not inflation_rate.empty:
            current_inflation = inflation_rate.iloc[-1]
            st.metric(
                "Current Inflation Rate",
                f"{current_inflation:.2f}%",
                delta=f"{current_inflation - inflation_rate.iloc[-13]:.2f}%" if len(inflation_rate) > 13 else None
            )
    
    with col2:
        if not m2_growth.empty:
            current_m2_growth = m2_growth.iloc[-1]
            st.metric(
                "M2 Growth Rate",
                f"{current_m2_growth:.2f}%",
                delta=f"{current_m2_growth - m2_growth.iloc[-13]:.2f}%" if len(m2_growth) > 13 else None
            )
    
    with col3:
        current_fed_rate = fed_data.iloc[-1]
        st.metric(
            "Fed Funds Rate",
            f"{current_fed_rate:.2f}%",
            delta=f"{current_fed_rate - fed_data.iloc[-13]:.2f}%" if len(fed_data) > 13 else None
        )
    
    with col4:
        if len(cpi_data) > 12:
            year_ago_cpi = cpi_data.iloc[-13]
            current_cpi = cpi_data.iloc[-1]
            purchasing_power = calculate_purchasing_power(year_ago_cpi, current_cpi)
            if purchasing_power:
                st.metric(
                    "Purchasing Power",
                    f"${purchasing_power:.2f}",
                    delta=f"${purchasing_power - 100:.2f}",
                    help="What $100 from a year ago is worth today"
                )
    
    # Charts
    st.header("📊 Data Visualization")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Inflation", "Money Supply", "Fed Rate", "Correlations"])
    
    with tab1:
        fig = create_inflation_chart(cpi_data, inflation_rate)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = create_m2_chart(m2_data, m2_growth)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = create_fed_rate_chart(fed_data)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = create_correlation_chart(inflation_rate, m2_growth, fed_data)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough overlapping data for correlation analysis")
    
    # Quick calculator
    st.header("🧮 Quick Calculator")
    calc_col1, calc_col2 = st.columns(2)
    
    with calc_col1:
        amount = st.number_input("Amount ($)", value=100, min_value=0.01)
        years_back = st.slider("Years ago", 1, 10, 1)
    
    with calc_col2:
        if len(cpi_data) > years_back * 12:
            past_cpi = cpi_data.iloc[-(years_back * 12)]
            current_cpi = cpi_data.iloc[-1]
            equivalent_value = calculate_purchasing_power(past_cpi, current_cpi, amount)
            
            if equivalent_value:
                st.success(f"${amount} from {years_back} year(s) ago is worth ${equivalent_value:.2f} today")
                inflation_total = ((current_cpi / past_cpi) - 1) * 100
                st.info(f"Total inflation over {years_back} year(s): {inflation_total:.2f}%")
    
    # Data info
    st.header("ℹ️ Data Sources")
    st.markdown("""
    - **CPI Data**: Consumer Price Index from Federal Reserve (FRED)
    - **M2 Data**: M2 Money Supply from Federal Reserve (FRED)
    - **Fed Rate**: Federal Funds Rate from Federal Reserve (FRED)
    - **Update Frequency**: Data refreshed every 5 minutes
    """)

if __name__ == "__main__":
    main()