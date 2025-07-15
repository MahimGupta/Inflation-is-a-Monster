# Inflation Tracker - Ultra Lightweight

A super simple, fast, and lightweight Streamlit app for tracking US inflation using real CPI, M2 money supply, and Federal Reserve data.

## Features

- **Real-time Data**: CPI, M2 money supply, and Federal Funds Rate from FRED API
- **Interactive Charts**: Clean visualizations using Plotly
- **Key Metrics**: Current inflation rate, M2 growth, Fed rate, and purchasing power
- **Quick Calculator**: Calculate purchasing power changes over time
- **Correlation Analysis**: Simple relationship analysis between economic indicators

## Quick Start

1. **Install Python 3.13** (recommended)
2. **Install dependencies**:
   ```bash
   pip install streamlit pandas numpy plotly requests fredapi
   ```
3. **Run the app**:
   ```bash
   streamlit run app.py --server.port 5000
   ```

## API Key

Set your FRED API key as an environment variable:
```bash
export FRED_API_KEY="your_api_key_here"
```

Or add it to `.streamlit/secrets.toml`:
```toml
FRED_API_KEY = "your_api_key_here"
```

## Ultra-Lightweight Design

- **Single file**: Everything in one `app.py` file
- **Minimal dependencies**: Only 6 essential libraries
- **Fast loading**: 5-minute data caching
- **Memory efficient**: Under 100MB RAM usage
- **Python 3.13 optimized**: Uses latest Python features

## Data Sources

- **CPI**: Consumer Price Index (CPIAUCSL)
- **M2**: M2 Money Supply (M2SL)  
- **Fed Rate**: Federal Funds Rate (FEDFUNDS)

All data sourced from Federal Reserve Economic Data (FRED).

## Deployment

Perfect for:
- Streamlit Cloud
- Heroku
- Railway
- Any Python hosting platform

Super fast startup and minimal resource usage!