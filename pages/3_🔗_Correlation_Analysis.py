import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from scipy import stats
import seaborn as sns
from utils.data_fetcher import DataFetcher
from utils.calculations import InflationCalculator
from utils.charts import ChartGenerator

st.set_page_config(page_title="Correlation Analysis - Inflation Monster", page_icon="🔗", layout="wide")

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
    st.title("🔗 Correlation Analysis")
    st.markdown("Analyze relationships between CPI, M2 Money Supply, and Bitcoin")
    
    # Sidebar controls
    st.sidebar.header("Analysis Controls")
    
    # Time period selector
    time_period = st.sidebar.selectbox(
        "Analysis Period",
        ["6 Months", "1 Year", "2 Years", "5 Years", "All Available"],
        index=1
    )
    
    # Correlation method
    correlation_method = st.sidebar.selectbox(
        "Correlation Method",
        ["Pearson", "Spearman", "Kendall"],
        index=0
    )
    
    # Rolling window for time-varying correlations
    rolling_window = st.sidebar.slider(
        "Rolling Window (days)",
        min_value=30,
        max_value=365,
        value=90,
        help="Window size for rolling correlation analysis"
    )
    
    # Convert time period to days
    period_mapping = {
        "6 Months": 180,
        "1 Year": 365,
        "2 Years": 730,
        "5 Years": 1825,
        "All Available": None
    }
    days = period_mapping[time_period]
    
    # Initialize components
    data_fetcher = get_data_fetcher()
    calculator = get_calculator()
    chart_gen = get_chart_generator()
    
    try:
        # Fetch data
        with st.spinner("Loading data for correlation analysis..."):
            cpi_data = data_fetcher.get_cpi_data(days=days)
            m2_data = data_fetcher.get_m2_data(days=days)
            bitcoin_data = data_fetcher.get_bitcoin_data(days=days)
        
        # Prepare data for correlation analysis
        if not cpi_data.empty and not bitcoin_data.empty:
            # Align data by dates
            combined_data = pd.DataFrame()
            
            # Resample to daily frequency and align
            if not cpi_data.empty:
                cpi_daily = cpi_data.resample('D').last().fillna(method='ffill')
                combined_data['CPI'] = cpi_daily['value']
            
            if not m2_data.empty:
                m2_daily = m2_data.resample('D').last().fillna(method='ffill')
                combined_data['M2'] = m2_daily['value']
            
            if not bitcoin_data.empty:
                btc_daily = bitcoin_data.resample('D').last().fillna(method='ffill')
                combined_data['Bitcoin'] = btc_daily['price']
            
            # Drop NaN values
            combined_data = combined_data.dropna()
            
            if len(combined_data) > 0:
                # Static Correlation Analysis
                st.header("📊 Static Correlation Matrix")
                
                # Calculate correlation matrix
                correlation_matrix = combined_data.corr(method=correlation_method.lower())
                
                # Create heatmap
                fig = go.Figure(data=go.Heatmap(
                    z=correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.columns,
                    colorscale='RdBu',
                    zmid=0,
                    text=correlation_matrix.values.round(3),
                    texttemplate="%{text}",
                    textfont={"size": 12},
                    hoverongaps=False
                ))
                
                fig.update_layout(
                    title=f"{correlation_method} Correlation Matrix",
                    height=400,
                    width=500
                )
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Correlation Interpretation")
                    
                    # Display correlation values with interpretation
                    correlations = []
                    for i in range(len(correlation_matrix.columns)):
                        for j in range(i+1, len(correlation_matrix.columns)):
                            var1 = correlation_matrix.columns[i]
                            var2 = correlation_matrix.columns[j]
                            corr_value = correlation_matrix.iloc[i, j]
                            correlations.append({
                                'Pair': f"{var1} vs {var2}",
                                'Correlation': corr_value,
                                'Strength': interpret_correlation(corr_value)
                            })
                    
                    corr_df = pd.DataFrame(correlations)
                    st.dataframe(corr_df, use_container_width=True)
                
                # Time-Varying Correlation Analysis
                st.header("📈 Rolling Correlation Analysis")
                
                # Calculate rolling correlations
                if 'CPI' in combined_data.columns and 'Bitcoin' in combined_data.columns:
                    rolling_corr_cpi_btc = combined_data['CPI'].rolling(window=rolling_window).corr(
                        combined_data['Bitcoin']
                    )
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=combined_data.index,
                        y=rolling_corr_cpi_btc,
                        mode='lines',
                        name=f'CPI vs Bitcoin ({rolling_window}d rolling)',
                        line=dict(color='blue')
                    ))
                    
                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig.add_hline(y=0.5, line_dash="dot", line_color="green", 
                                 annotation_text="Strong Positive")
                    fig.add_hline(y=-0.5, line_dash="dot", line_color="red", 
                                 annotation_text="Strong Negative")
                    
                    fig.update_layout(
                        title=f"Rolling Correlation: CPI vs Bitcoin ({rolling_window} days)",
                        xaxis_title="Date",
                        yaxis_title="Correlation Coefficient",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Multiple rolling correlations
                if len(combined_data.columns) >= 3:
                    st.subheader("Multiple Rolling Correlations")
                    
                    fig = go.Figure()
                    
                    # CPI vs Bitcoin
                    if 'CPI' in combined_data.columns and 'Bitcoin' in combined_data.columns:
                        rolling_corr = combined_data['CPI'].rolling(window=rolling_window).corr(
                            combined_data['Bitcoin']
                        )
                        fig.add_trace(go.Scatter(
                            x=combined_data.index,
                            y=rolling_corr,
                            mode='lines',
                            name='CPI vs Bitcoin',
                            line=dict(color='blue')
                        ))
                    
                    # CPI vs M2
                    if 'CPI' in combined_data.columns and 'M2' in combined_data.columns:
                        rolling_corr = combined_data['CPI'].rolling(window=rolling_window).corr(
                            combined_data['M2']
                        )
                        fig.add_trace(go.Scatter(
                            x=combined_data.index,
                            y=rolling_corr,
                            mode='lines',
                            name='CPI vs M2',
                            line=dict(color='green')
                        ))
                    
                    # Bitcoin vs M2
                    if 'Bitcoin' in combined_data.columns and 'M2' in combined_data.columns:
                        rolling_corr = combined_data['Bitcoin'].rolling(window=rolling_window).corr(
                            combined_data['M2']
                        )
                        fig.add_trace(go.Scatter(
                            x=combined_data.index,
                            y=rolling_corr,
                            mode='lines',
                            name='Bitcoin vs M2',
                            line=dict(color='orange')
                        ))
                    
                    fig.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig.update_layout(
                        title=f"Rolling Correlations ({rolling_window} days)",
                        xaxis_title="Date",
                        yaxis_title="Correlation Coefficient",
                        height=500
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Scatter Plot Analysis
                st.header("🎯 Scatter Plot Analysis")
                
                tab1, tab2, tab3 = st.tabs(["CPI vs Bitcoin", "CPI vs M2", "Bitcoin vs M2"])
                
                with tab1:
                    if 'CPI' in combined_data.columns and 'Bitcoin' in combined_data.columns:
                        fig = px.scatter(
                            combined_data,
                            x='CPI',
                            y='Bitcoin',
                            title='CPI vs Bitcoin Price',
                            trendline='ols'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Calculate regression statistics
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            combined_data['CPI'].dropna(),
                            combined_data['Bitcoin'].dropna()
                        )
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("R-squared", f"{r_value**2:.4f}")
                        with col2:
                            st.metric("P-value", f"{p_value:.4f}")
                        with col3:
                            st.metric("Slope", f"{slope:.2f}")
                
                with tab2:
                    if 'CPI' in combined_data.columns and 'M2' in combined_data.columns:
                        fig = px.scatter(
                            combined_data,
                            x='CPI',
                            y='M2',
                            title='CPI vs M2 Money Supply',
                            trendline='ols'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            combined_data['CPI'].dropna(),
                            combined_data['M2'].dropna()
                        )
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("R-squared", f"{r_value**2:.4f}")
                        with col2:
                            st.metric("P-value", f"{p_value:.4f}")
                        with col3:
                            st.metric("Slope", f"{slope:.2f}")
                
                with tab3:
                    if 'Bitcoin' in combined_data.columns and 'M2' in combined_data.columns:
                        fig = px.scatter(
                            combined_data,
                            x='Bitcoin',
                            y='M2',
                            title='Bitcoin vs M2 Money Supply',
                            trendline='ols'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        slope, intercept, r_value, p_value, std_err = stats.linregress(
                            combined_data['Bitcoin'].dropna(),
                            combined_data['M2'].dropna()
                        )
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("R-squared", f"{r_value**2:.4f}")
                        with col2:
                            st.metric("P-value", f"{p_value:.4f}")
                        with col3:
                            st.metric("Slope", f"{slope:.2f}")
                
                # Statistical Tests
                st.header("📋 Statistical Tests")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Correlation Significance Tests")
                    
                    # Test correlations for significance
                    for i, pair in enumerate(corr_df['Pair']):
                        corr_val = corr_df.iloc[i]['Correlation']
                        n = len(combined_data.dropna())
                        
                        # Calculate t-statistic
                        t_stat = corr_val * np.sqrt((n-2) / (1 - corr_val**2))
                        p_val = 2 * (1 - stats.t.cdf(abs(t_stat), n-2))
                        
                        significance = "Significant" if p_val < 0.05 else "Not Significant"
                        st.write(f"**{pair}**: {significance} (p = {p_val:.4f})")
                
                with col2:
                    st.subheader("Data Summary")
                    st.write(f"**Sample Size**: {len(combined_data)} observations")
                    st.write(f"**Date Range**: {combined_data.index.min().strftime('%Y-%m-%d')} to {combined_data.index.max().strftime('%Y-%m-%d')}")
                    st.write(f"**Correlation Method**: {correlation_method}")
                    st.write(f"**Rolling Window**: {rolling_window} days")
            
            else:
                st.error("No overlapping data available for correlation analysis.")
        
        else:
            st.error("Insufficient data for correlation analysis.")
    
    except Exception as e:
        st.error(f"Error in correlation analysis: {str(e)}")
        st.info("Please check your data sources and try again.")

def interpret_correlation(corr_value):
    """Interpret correlation strength"""
    abs_corr = abs(corr_value)
    
    if abs_corr >= 0.8:
        return "Very Strong"
    elif abs_corr >= 0.6:
        return "Strong"
    elif abs_corr >= 0.4:
        return "Moderate"
    elif abs_corr >= 0.2:
        return "Weak"
    else:
        return "Very Weak"

if __name__ == "__main__":
    main()
