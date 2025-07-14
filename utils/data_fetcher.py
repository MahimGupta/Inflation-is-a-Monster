import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import os
from fredapi import Fred
import time

class DataFetcher:
    """Handles data fetching from various APIs"""
    
    def __init__(self):
        self.fred_api_key = os.getenv("FRED_API_KEY", "928bfef823af054db951f38d94f04afe")
        self.fred = Fred(api_key=self.fred_api_key)
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_cpi_data(_self, days=365):
        """Fetch CPI data from FRED API"""
        try:
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days) if days else datetime(1950, 1, 1)
            
            # Fetch CPI data (Consumer Price Index for All Urban Consumers)
            cpi_data = _self.fred.get_series(
                'CPIAUCSL',
                start=start_date,
                end=end_date
            )
            
            if cpi_data.empty:
                st.warning("No CPI data available for the selected period")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'date': cpi_data.index,
                'value': cpi_data.values
            })
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching CPI data: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_m2_data(_self, days=365):
        """Fetch M2 Money Supply data from FRED API"""
        try:
            # Calculate start date
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days) if days else datetime(1950, 1, 1)
            
            # Fetch M2 Money Supply data
            m2_data = _self.fred.get_series(
                'M2SL',
                start=start_date,
                end=end_date
            )
            
            if m2_data.empty:
                st.warning("No M2 data available for the selected period")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame({
                'date': m2_data.index,
                'value': m2_data.values
            })
            df.set_index('date', inplace=True)
            
            return df
            
        except Exception as e:
            st.error(f"Error fetching M2 data: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_bitcoin_data(_self, days=365):
        """Fetch Bitcoin price data from CoinGecko API"""
        try:
            # CoinGecko API endpoint for historical data
            if days <= 90:
                # For periods <= 90 days, use hourly data
                url = f"{_self.coingecko_base_url}/coins/bitcoin/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'daily'
                }
            else:
                # For longer periods, use daily data
                url = f"{_self.coingecko_base_url}/coins/bitcoin/market_chart"
                params = {
                    'vs_currency': 'usd',
                    'days': days,
                    'interval': 'daily'
                }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'prices' not in data:
                st.warning("No Bitcoin price data available")
                return pd.DataFrame()
            
            # Extract price data
            prices = data['prices']
            
            # Convert to DataFrame
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('date', inplace=True)
            df.drop('timestamp', axis=1, inplace=True)
            
            return df
            
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching Bitcoin data: {str(e)}")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error processing Bitcoin data: {str(e)}")
            return pd.DataFrame()
    
    @st.cache_data(ttl=3600)  # Cache for 1 hour
    def get_economic_indicators(_self):
        """Fetch additional economic indicators"""
        try:
            indicators = {}
            
            # GDP
            try:
                gdp_data = _self.fred.get_series('GDP', limit=4)  # Last 4 quarters
                if not gdp_data.empty:
                    indicators['GDP'] = {
                        'value': gdp_data.iloc[-1],
                        'change': ((gdp_data.iloc[-1] - gdp_data.iloc[-2]) / gdp_data.iloc[-2]) * 100 if len(gdp_data) > 1 else 0
                    }
            except:
                pass
            
            # Unemployment Rate
            try:
                unemployment_data = _self.fred.get_series('UNRATE', limit=12)  # Last 12 months
                if not unemployment_data.empty:
                    indicators['Unemployment'] = {
                        'value': unemployment_data.iloc[-1],
                        'change': unemployment_data.iloc[-1] - unemployment_data.iloc[-2] if len(unemployment_data) > 1 else 0
                    }
            except:
                pass
            
            # Federal Funds Rate
            try:
                fed_rate_data = _self.fred.get_series('FEDFUNDS', limit=12)  # Last 12 months
                if not fed_rate_data.empty:
                    indicators['Fed_Rate'] = {
                        'value': fed_rate_data.iloc[-1],
                        'change': fed_rate_data.iloc[-1] - fed_rate_data.iloc[-2] if len(fed_rate_data) > 1 else 0
                    }
            except:
                pass
            
            return indicators
            
        except Exception as e:
            st.error(f"Error fetching economic indicators: {str(e)}")
            return {}
    
    def get_data_status(self):
        """Check the status of data sources"""
        status = {
            'fred_api': False,
            'coingecko_api': False,
            'last_updated': None
        }
        
        # Test FRED API
        try:
            test_data = self.fred.get_series('CPIAUCSL', limit=1)
            if not test_data.empty:
                status['fred_api'] = True
        except:
            pass
        
        # Test CoinGecko API
        try:
            response = requests.get(f"{self.coingecko_base_url}/ping", timeout=10)
            if response.status_code == 200:
                status['coingecko_api'] = True
        except:
            pass
        
        status['last_updated'] = datetime.now()
        
        return status
    
    def validate_data(self, data, data_type):
        """Validate fetched data"""
        if data.empty:
            return False, f"No {data_type} data available"
        
        # Check for missing values
        if data.isnull().all().any():
            return False, f"{data_type} data contains only null values"
        
        # Check for reasonable date range
        if data.index.max() < datetime.now() - timedelta(days=30):
            return False, f"{data_type} data appears to be outdated"
        
        return True, "Data validation passed"
