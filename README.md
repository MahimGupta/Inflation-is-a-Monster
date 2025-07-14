# Inflation Monster - Streamlit Application

## Overview

Inflation Monster is a comprehensive Streamlit-based web application for analyzing US inflation trends and economic indicators. The application provides real-time data visualization, historical analysis, correlation studies, and calculation tools for inflation-related metrics.

## Features

- **Real-time Dashboard**: Live CPI, M2 money supply, and Bitcoin price metrics
- **Historical Analysis**: Long-term trend analysis with moving averages and volatility studies
- **Correlation Analysis**: Analyze relationships between different economic indicators
- **Inflation Calculator**: Calculate purchasing power changes over time
- **Data Export**: Export data in CSV, Excel, and JSON formats

## Data Sources

- **CPI Data**: Federal Reserve Economic Data (FRED) API
- **M2 Money Supply**: Federal Reserve Economic Data (FRED) API
- **Bitcoin Prices**: CoinGecko API

## Deployment

### Streamlit Cloud Deployment

1. Fork this repository
2. Connect your GitHub account to Streamlit Cloud
3. Add your FRED API key in the Streamlit Cloud secrets:
   - Go to your app settings in Streamlit Cloud
   - Add a new secret: `FRED_API_KEY = "your_api_key_here"`
4. Deploy the application

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export FRED_API_KEY="your_fred_api_key"
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Configuration

The application uses `.streamlit/config.toml` for configuration settings and `.streamlit/secrets.toml` for sensitive information like API keys.

## API Keys

To use this application, you need:
- FRED API Key (free from Federal Reserve Economic Data)

## License

MIT License