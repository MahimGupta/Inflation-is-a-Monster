import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class InflationCalculator:
    """Handles inflation calculations and analysis"""
    
    def __init__(self):
        pass
    
    def calculate_yoy_inflation(self, cpi_data, periods=12):
        """Calculate year-over-year inflation rate"""
        try:
            if len(cpi_data) < periods:
                return 0.0
            
            latest_cpi = cpi_data['value'].iloc[-1]
            previous_cpi = cpi_data['value'].iloc[-periods]
            
            yoy_rate = ((latest_cpi - previous_cpi) / previous_cpi) * 100
            return yoy_rate
            
        except Exception as e:
            st.error(f"Error calculating YoY inflation: {str(e)}")
            return 0.0
    
    def calculate_money_supply_growth(self, m2_data, periods=12):
        """Calculate M2 money supply growth rate"""
        try:
            if len(m2_data) < periods:
                return 0.0
            
            latest_m2 = m2_data['value'].iloc[-1]
            previous_m2 = m2_data['value'].iloc[-periods]
            
            growth_rate = ((latest_m2 - previous_m2) / previous_m2) * 100
            return growth_rate
            
        except Exception as e:
            st.error(f"Error calculating M2 growth: {str(e)}")
            return 0.0
    
    def calculate_purchasing_power(self, cpi_data, amount, from_date, to_date):
        """Calculate purchasing power between two dates"""
        try:
            # Convert dates to datetime if needed
            if isinstance(from_date, str):
                from_date = datetime.strptime(from_date, '%Y-%m-%d')
            if isinstance(to_date, str):
                to_date = datetime.strptime(to_date, '%Y-%m-%d')
            
            # Find CPI values for the dates
            from_cpi = self._get_cpi_for_date(cpi_data, from_date)
            to_cpi = self._get_cpi_for_date(cpi_data, to_date)
            
            if from_cpi is None or to_cpi is None:
                return {
                    'equivalent_value': amount,
                    'inflation_rate': 0.0,
                    'purchasing_power_change': 0.0
                }
            
            # Calculate equivalent value
            equivalent_value = amount * (to_cpi / from_cpi)
            
            # Calculate inflation rate
            inflation_rate = ((to_cpi - from_cpi) / from_cpi) * 100
            
            # Calculate purchasing power change
            purchasing_power_change = ((equivalent_value - amount) / amount) * 100
            
            return {
                'equivalent_value': equivalent_value,
                'inflation_rate': inflation_rate,
                'purchasing_power_change': purchasing_power_change
            }
            
        except Exception as e:
            st.error(f"Error calculating purchasing power: {str(e)}")
            return {
                'equivalent_value': amount,
                'inflation_rate': 0.0,
                'purchasing_power_change': 0.0
            }
    
    def calculate_trend_statistics(self, data_series):
        """Calculate trend statistics for a data series"""
        try:
            # Annual growth rate
            if len(data_series) >= 12:
                annual_growth = ((data_series.iloc[-1] / data_series.iloc[-12]) - 1) * 100
            else:
                annual_growth = 0.0
            
            # Volatility (standard deviation of monthly changes)
            monthly_changes = data_series.pct_change().dropna()
            volatility = monthly_changes.std() * np.sqrt(12) * 100  # Annualized
            
            # Trend direction
            if len(data_series) >= 3:
                recent_trend = data_series.iloc[-3:].pct_change().mean() * 100
                if recent_trend > 0.1:
                    trend_direction = "Increasing"
                elif recent_trend < -0.1:
                    trend_direction = "Decreasing"
                else:
                    trend_direction = "Stable"
            else:
                trend_direction = "Insufficient Data"
            
            return {
                'annual_growth': annual_growth,
                'volatility': volatility,
                'trend_direction': trend_direction
            }
            
        except Exception as e:
            st.error(f"Error calculating trend statistics: {str(e)}")
            return {
                'annual_growth': 0.0,
                'volatility': 0.0,
                'trend_direction': "Error"
            }
    
    def calculate_average_inflation(self, cpi_data, years=10):
        """Calculate average inflation rate over specified years"""
        try:
            if len(cpi_data) < 12:
                return 3.0  # Default assumption
            
            # Calculate monthly inflation rates
            monthly_inflation = cpi_data['value'].pct_change().dropna()
            
            # Get last N years of data
            periods = min(years * 12, len(monthly_inflation))
            recent_inflation = monthly_inflation.iloc[-periods:]
            
            # Calculate annualized average
            avg_monthly = recent_inflation.mean()
            avg_annual = (((1 + avg_monthly) ** 12) - 1) * 100
            
            return avg_annual
            
        except Exception as e:
            st.error(f"Error calculating average inflation: {str(e)}")
            return 3.0
    
    def calculate_inflation_scenarios(self, initial_amount, years, expected_inflation, historical_inflation):
        """Calculate inflation impact scenarios"""
        try:
            # Expected inflation scenario
            expected_value = initial_amount * ((1 - expected_inflation/100) ** years)
            
            # Historical inflation scenario
            historical_value = initial_amount * ((1 - historical_inflation/100) ** years)
            
            return {
                'expected_value': expected_value,
                'historical_value': historical_value,
                'historical_inflation': historical_inflation,
                'expected_inflation': expected_inflation
            }
            
        except Exception as e:
            st.error(f"Error calculating inflation scenarios: {str(e)}")
            return {
                'expected_value': initial_amount,
                'historical_value': initial_amount,
                'historical_inflation': 3.0,
                'expected_inflation': expected_inflation
            }
    
    def calculate_future_value(self, principal, monthly_contribution, return_rate, inflation_rate, years):
        """Calculate future value with inflation adjustment"""
        try:
            monthly_return = return_rate / 100 / 12
            monthly_inflation = inflation_rate / 100 / 12
            months = years * 12
            
            # Calculate nominal future value
            nominal_value = principal
            total_contributions = principal
            
            # Track trajectories
            nominal_trajectory = [principal]
            real_trajectory = [principal]
            contributions_trajectory = [principal]
            
            for month in range(1, months + 1):
                # Add monthly contribution
                nominal_value += monthly_contribution
                total_contributions += monthly_contribution
                
                # Apply investment return
                nominal_value *= (1 + monthly_return)
                
                # Track trajectories
                if month % 12 == 0:  # Annual data points
                    year = month // 12
                    real_value = nominal_value / ((1 + monthly_inflation) ** month)
                    
                    nominal_trajectory.append(nominal_value)
                    real_trajectory.append(real_value)
                    contributions_trajectory.append(total_contributions)
            
            # Final calculations
            final_real_value = nominal_value / ((1 + monthly_inflation) ** months)
            investment_gains = nominal_value - total_contributions
            
            return {
                'nominal_value': nominal_value,
                'real_value': final_real_value,
                'total_contributions': total_contributions,
                'investment_gains': investment_gains,
                'nominal_trajectory': nominal_trajectory,
                'real_trajectory': real_trajectory,
                'contributions_trajectory': contributions_trajectory
            }
            
        except Exception as e:
            st.error(f"Error calculating future value: {str(e)}")
            return {
                'nominal_value': principal,
                'real_value': principal,
                'total_contributions': principal,
                'investment_gains': 0,
                'nominal_trajectory': [principal],
                'real_trajectory': [principal],
                'contributions_trajectory': [principal]
            }
    
    def compare_scenarios(self, base_amount, years, cash_inflation, investment_return, 
                         investment_inflation, alt_return, alt_inflation):
        """Compare multiple investment scenarios"""
        try:
            # Cash scenario (just inflation erosion)
            cash_real = base_amount * ((1 - cash_inflation/100) ** years)
            
            # Investment scenario
            investment_nominal = base_amount * ((1 + investment_return/100) ** years)
            investment_real = investment_nominal * ((1 - investment_inflation/100) ** years)
            
            # Alternative asset scenario
            alt_nominal = base_amount * ((1 + alt_return/100) ** years)
            alt_real = alt_nominal * ((1 - alt_inflation/100) ** years)
            
            # Generate trajectories
            years_range = list(range(years + 1))
            
            cash_trajectory = [base_amount * ((1 - cash_inflation/100) ** year) for year in years_range]
            investment_trajectory = [base_amount * ((1 + investment_return/100) ** year) * ((1 - investment_inflation/100) ** year) for year in years_range]
            alt_trajectory = [base_amount * ((1 + alt_return/100) ** year) * ((1 - alt_inflation/100) ** year) for year in years_range]
            
            return {
                'cash_real': cash_real,
                'investment_real': investment_real,
                'alternative_real': alt_real,
                'cash_trajectory': cash_trajectory,
                'investment_trajectory': investment_trajectory,
                'alternative_trajectory': alt_trajectory
            }
            
        except Exception as e:
            st.error(f"Error comparing scenarios: {str(e)}")
            return {
                'cash_real': base_amount,
                'investment_real': base_amount,
                'alternative_real': base_amount,
                'cash_trajectory': [base_amount],
                'investment_trajectory': [base_amount],
                'alternative_trajectory': [base_amount]
            }
    
    def calculate_correlation_metrics(self, data1, data2, window=30):
        """Calculate correlation metrics between two datasets"""
        try:
            # Align data
            aligned_data = pd.DataFrame({
                'series1': data1,
                'series2': data2
            }).dropna()
            
            if len(aligned_data) < window:
                return {
                    'correlation': 0.0,
                    'rolling_correlation': pd.Series(),
                    'p_value': 1.0
                }
            
            # Static correlation
            correlation = aligned_data['series1'].corr(aligned_data['series2'])
            
            # Rolling correlation
            rolling_corr = aligned_data['series1'].rolling(window=window).corr(aligned_data['series2'])
            
            # Statistical significance (simplified)
            n = len(aligned_data)
            t_stat = correlation * np.sqrt((n-2) / (1 - correlation**2))
            p_value = 2 * (1 - abs(t_stat))  # Simplified p-value calculation
            
            return {
                'correlation': correlation,
                'rolling_correlation': rolling_corr,
                'p_value': p_value
            }
            
        except Exception as e:
            st.error(f"Error calculating correlation: {str(e)}")
            return {
                'correlation': 0.0,
                'rolling_correlation': pd.Series(),
                'p_value': 1.0
            }
    
    def _get_cpi_for_date(self, cpi_data, target_date):
        """Get CPI value for a specific date (with interpolation if needed)"""
        try:
            # Convert target_date to pandas datetime
            target_date = pd.to_datetime(target_date)
            
            # Find the closest date
            closest_date = cpi_data.index[cpi_data.index.get_indexer([target_date], method='nearest')[0]]
            
            return cpi_data.loc[closest_date, 'value']
            
        except Exception as e:
            return None
