import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from utils.data_fetcher import DataFetcher
from utils.calculations import InflationCalculator

st.set_page_config(page_title="Inflation Calculator - Inflation Monster", page_icon="🧮", layout="wide")

@st.cache_resource
def get_data_fetcher():
    return DataFetcher()

@st.cache_resource
def get_calculator():
    return InflationCalculator()

def main():
    st.title("🧮 Inflation Calculator")
    st.markdown("Calculate purchasing power, inflation impact, and future value projections")
    
    # Initialize components
    data_fetcher = get_data_fetcher()
    calculator = get_calculator()
    
    # Load CPI data for calculations
    try:
        with st.spinner("Loading CPI data..."):
            cpi_data = data_fetcher.get_cpi_data(days=3650)  # 10 years of data
        
        if cpi_data.empty:
            st.error("Unable to load CPI data. Please check your connection.")
            return
        
        # Create tabs for different calculators
        tab1, tab2, tab3, tab4 = st.tabs([
            "💰 Purchasing Power",
            "📈 Inflation Impact",
            "🔮 Future Value",
            "📊 Comparison Tool"
        ])
        
        # Tab 1: Purchasing Power Calculator
        with tab1:
            st.header("💰 Purchasing Power Calculator")
            st.markdown("Calculate how much your money was worth in the past or will be worth in the future")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Input Parameters")
                
                # Amount input
                amount = st.number_input(
                    "Amount ($)",
                    min_value=0.01,
                    value=100.0,
                    step=0.01,
                    help="Enter the dollar amount you want to analyze"
                )
                
                # Date selection
                min_date = cpi_data.index.min().date()
                max_date = cpi_data.index.max().date()
                
                from_date = st.date_input(
                    "From Date",
                    value=datetime.now().date() - timedelta(days=365),
                    min_value=min_date,
                    max_value=max_date
                )
                
                to_date = st.date_input(
                    "To Date",
                    value=datetime.now().date(),
                    min_value=min_date,
                    max_value=max_date
                )
                
                if st.button("Calculate Purchasing Power", type="primary"):
                    if from_date < to_date:
                        result = calculator.calculate_purchasing_power(
                            cpi_data, amount, from_date, to_date
                        )
                        
                        st.session_state.purchasing_power_result = result
                    else:
                        st.error("'From Date' must be earlier than 'To Date'")
            
            with col2:
                st.subheader("Results")
                
                if hasattr(st.session_state, 'purchasing_power_result'):
                    result = st.session_state.purchasing_power_result
                    
                    # Display results
                    st.metric(
                        "Equivalent Value",
                        f"${result['equivalent_value']:.2f}",
                        delta=f"${result['equivalent_value'] - amount:.2f}"
                    )
                    
                    st.metric(
                        "Inflation Rate",
                        f"{result['inflation_rate']:.2f}%"
                    )
                    
                    st.metric(
                        "Purchasing Power Change",
                        f"{result['purchasing_power_change']:.2f}%"
                    )
                    
                    # Interpretation
                    if result['purchasing_power_change'] > 0:
                        st.success("Your money has gained purchasing power!")
                    elif result['purchasing_power_change'] < 0:
                        st.warning("Your money has lost purchasing power due to inflation.")
                    else:
                        st.info("No change in purchasing power.")
                    
                    # Visual representation
                    fig = go.Figure()
                    
                    categories = ['Original Value', 'Equivalent Value']
                    values = [amount, result['equivalent_value']]
                    colors = ['blue', 'red' if result['equivalent_value'] > amount else 'green']
                    
                    fig.add_trace(go.Bar(
                        x=categories,
                        y=values,
                        marker_color=colors,
                        text=[f"${v:.2f}" for v in values],
                        textposition='auto'
                    ))
                    
                    fig.update_layout(
                        title="Purchasing Power Comparison",
                        yaxis_title="Value ($)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Enter parameters and click 'Calculate Purchasing Power' to see results.")
        
        # Tab 2: Inflation Impact Calculator
        with tab2:
            st.header("📈 Inflation Impact Calculator")
            st.markdown("Analyze the cumulative impact of inflation on your finances")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Scenario Parameters")
                
                # Initial amount
                initial_amount = st.number_input(
                    "Initial Amount ($)",
                    min_value=0.01,
                    value=10000.0,
                    step=100.0
                )
                
                # Time period
                years = st.slider(
                    "Time Period (Years)",
                    min_value=1,
                    max_value=30,
                    value=10
                )
                
                # Expected inflation rate
                expected_inflation = st.slider(
                    "Expected Annual Inflation Rate (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=3.0,
                    step=0.1
                )
                
                # Calculate different scenarios
                if st.button("Calculate Inflation Impact", type="primary"):
                    # Historical average inflation
                    historical_avg = calculator.calculate_average_inflation(cpi_data)
                    
                    # Calculate scenarios
                    scenarios = calculator.calculate_inflation_scenarios(
                        initial_amount, years, expected_inflation, historical_avg
                    )
                    
                    st.session_state.inflation_scenarios = scenarios
            
            with col2:
                st.subheader("Impact Analysis")
                
                if hasattr(st.session_state, 'inflation_scenarios'):
                    scenarios = st.session_state.inflation_scenarios
                    
                    # Display scenario results
                    st.metric(
                        "With Expected Inflation",
                        f"${scenarios['expected_value']:.2f}",
                        delta=f"-${initial_amount - scenarios['expected_value']:.2f}"
                    )
                    
                    st.metric(
                        "With Historical Average",
                        f"${scenarios['historical_value']:.2f}",
                        delta=f"-${initial_amount - scenarios['historical_value']:.2f}"
                    )
                    
                    st.metric(
                        "Historical Average Inflation",
                        f"{scenarios['historical_inflation']:.2f}%"
                    )
                    
                    # Create projection chart
                    years_range = list(range(0, years + 1))
                    expected_values = [initial_amount * (1 - expected_inflation/100)**year for year in years_range]
                    historical_values = [initial_amount * (1 - scenarios['historical_inflation']/100)**year for year in years_range]
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=years_range,
                        y=expected_values,
                        mode='lines+markers',
                        name=f'Expected Inflation ({expected_inflation}%)',
                        line=dict(color='red')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=years_range,
                        y=historical_values,
                        mode='lines+markers',
                        name=f'Historical Average ({scenarios["historical_inflation"]:.1f}%)',
                        line=dict(color='blue')
                    ))
                    
                    fig.update_layout(
                        title="Purchasing Power Erosion Over Time",
                        xaxis_title="Years",
                        yaxis_title="Purchasing Power ($)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Set parameters and click 'Calculate Inflation Impact' to see projections.")
        
        # Tab 3: Future Value Calculator
        with tab3:
            st.header("🔮 Future Value Calculator")
            st.markdown("Project future values considering inflation and investment returns")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Investment Parameters")
                
                # Principal amount
                principal = st.number_input(
                    "Principal Amount ($)",
                    min_value=0.01,
                    value=10000.0,
                    step=100.0
                )
                
                # Monthly contributions
                monthly_contribution = st.number_input(
                    "Monthly Contribution ($)",
                    min_value=0.0,
                    value=500.0,
                    step=50.0
                )
                
                # Expected return rate
                return_rate = st.slider(
                    "Expected Annual Return (%)",
                    min_value=0.0,
                    max_value=20.0,
                    value=7.0,
                    step=0.1
                )
                
                # Inflation rate
                inflation_rate = st.slider(
                    "Expected Inflation Rate (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=3.0,
                    step=0.1
                )
                
                # Time horizon
                time_horizon = st.slider(
                    "Time Horizon (Years)",
                    min_value=1,
                    max_value=40,
                    value=20
                )
                
                if st.button("Calculate Future Value", type="primary"):
                    future_value_result = calculator.calculate_future_value(
                        principal, monthly_contribution, return_rate, inflation_rate, time_horizon
                    )
                    
                    st.session_state.future_value_result = future_value_result
            
            with col2:
                st.subheader("Projection Results")
                
                if hasattr(st.session_state, 'future_value_result'):
                    result = st.session_state.future_value_result
                    
                    # Display key metrics
                    st.metric(
                        "Nominal Future Value",
                        f"${result['nominal_value']:,.2f}"
                    )
                    
                    st.metric(
                        "Real Future Value",
                        f"${result['real_value']:,.2f}",
                        help="Adjusted for inflation"
                    )
                    
                    st.metric(
                        "Total Contributions",
                        f"${result['total_contributions']:,.2f}"
                    )
                    
                    st.metric(
                        "Investment Gains",
                        f"${result['investment_gains']:,.2f}"
                    )
                    
                    # Create growth chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=list(range(time_horizon + 1)),
                        y=result['nominal_trajectory'],
                        mode='lines',
                        name='Nominal Value',
                        line=dict(color='blue')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=list(range(time_horizon + 1)),
                        y=result['real_trajectory'],
                        mode='lines',
                        name='Real Value (Inflation-Adjusted)',
                        line=dict(color='red')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=list(range(time_horizon + 1)),
                        y=result['contributions_trajectory'],
                        mode='lines',
                        name='Total Contributions',
                        line=dict(color='green', dash='dash')
                    ))
                    
                    fig.update_layout(
                        title="Investment Growth Projection",
                        xaxis_title="Years",
                        yaxis_title="Value ($)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Set parameters and click 'Calculate Future Value' to see projections.")
        
        # Tab 4: Comparison Tool
        with tab4:
            st.header("📊 Comparison Tool")
            st.markdown("Compare multiple scenarios and investment options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Scenario Comparison")
                
                # Common parameters
                base_amount = st.number_input(
                    "Base Amount ($)",
                    min_value=0.01,
                    value=10000.0,
                    step=100.0
                )
                
                comparison_years = st.slider(
                    "Comparison Period (Years)",
                    min_value=1,
                    max_value=30,
                    value=10
                )
                
                # Scenario 1
                st.subheader("Scenario 1: Cash")
                cash_inflation = st.slider(
                    "Cash Inflation Rate (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=3.0,
                    step=0.1,
                    key="cash_inflation"
                )
                
                # Scenario 2
                st.subheader("Scenario 2: Investment")
                investment_return = st.slider(
                    "Investment Return (%)",
                    min_value=0.0,
                    max_value=15.0,
                    value=7.0,
                    step=0.1
                )
                
                investment_inflation = st.slider(
                    "Investment Inflation Rate (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=3.0,
                    step=0.1,
                    key="investment_inflation"
                )
                
                # Scenario 3
                st.subheader("Scenario 3: Alternative Asset")
                alt_return = st.slider(
                    "Alternative Asset Return (%)",
                    min_value=-10.0,
                    max_value=20.0,
                    value=10.0,
                    step=0.1
                )
                
                alt_inflation = st.slider(
                    "Alternative Asset Inflation Rate (%)",
                    min_value=0.0,
                    max_value=10.0,
                    value=3.0,
                    step=0.1,
                    key="alt_inflation"
                )
                
                if st.button("Compare Scenarios", type="primary"):
                    comparison_result = calculator.compare_scenarios(
                        base_amount, comparison_years,
                        cash_inflation, investment_return, investment_inflation,
                        alt_return, alt_inflation
                    )
                    
                    st.session_state.comparison_result = comparison_result
            
            with col2:
                st.subheader("Comparison Results")
                
                if hasattr(st.session_state, 'comparison_result'):
                    result = st.session_state.comparison_result
                    
                    # Display final values
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric(
                            "Cash (Real Value)",
                            f"${result['cash_real']:.2f}",
                            delta=f"${result['cash_real'] - base_amount:.2f}"
                        )
                    
                    with col_b:
                        st.metric(
                            "Investment (Real Value)",
                            f"${result['investment_real']:.2f}",
                            delta=f"${result['investment_real'] - base_amount:.2f}"
                        )
                    
                    with col_c:
                        st.metric(
                            "Alternative (Real Value)",
                            f"${result['alternative_real']:.2f}",
                            delta=f"${result['alternative_real'] - base_amount:.2f}"
                        )
                    
                    # Create comparison chart
                    fig = go.Figure()
                    
                    years_range = list(range(comparison_years + 1))
                    
                    fig.add_trace(go.Scatter(
                        x=years_range,
                        y=result['cash_trajectory'],
                        mode='lines',
                        name='Cash (Real Value)',
                        line=dict(color='red')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=years_range,
                        y=result['investment_trajectory'],
                        mode='lines',
                        name='Investment (Real Value)',
                        line=dict(color='blue')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=years_range,
                        y=result['alternative_trajectory'],
                        mode='lines',
                        name='Alternative Asset (Real Value)',
                        line=dict(color='green')
                    ))
                    
                    fig.update_layout(
                        title="Scenario Comparison (Real Values)",
                        xaxis_title="Years",
                        yaxis_title="Real Value ($)",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Best scenario
                    best_scenario = max(
                        [('Cash', result['cash_real']), 
                         ('Investment', result['investment_real']), 
                         ('Alternative', result['alternative_real'])],
                        key=lambda x: x[1]
                    )
                    
                    st.success(f"Best performing scenario: **{best_scenario[0]}** with ${best_scenario[1]:.2f}")
                else:
                    st.info("Set parameters and click 'Compare Scenarios' to see results.")
    
    except Exception as e:
        st.error(f"Error in inflation calculator: {str(e)}")
        st.info("Please check your data connection and try again.")

if __name__ == "__main__":
    main()
