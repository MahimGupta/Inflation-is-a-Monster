# Inflation Monster - Streamlit Application

## Overview

Inflation Monster is a comprehensive Streamlit-based web application for analyzing US inflation trends and economic indicators. The application provides real-time data visualization, historical analysis, correlation studies, and calculation tools for inflation-related metrics. It integrates multiple data sources including Federal Reserve Economic Data (FRED) for CPI and M2 money supply, and CoinGecko API for Bitcoin price data.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit with multi-page application structure
- **Layout**: Wide layout with expandable sidebar navigation
- **Visualization**: Plotly for interactive charts and graphs
- **State Management**: Streamlit's native session state and caching mechanisms

### Backend Architecture
- **Structure**: Modular utility-based architecture with three main utility modules
- **Data Processing**: Pandas for data manipulation and NumPy for calculations
- **API Integration**: Direct API calls using requests library and specialized clients (fredapi for FRED)
- **Caching Strategy**: Streamlit's `@st.cache_resource` and `@st.cache_data` decorators

### Page Structure
The application uses Streamlit's multi-page feature with the following pages:
1. **Main App** (`app.py`) - Landing page with navigation
2. **Dashboard** (`pages/1_📊_Dashboard.py`) - Real-time metrics and key indicators
3. **Historical Analysis** (`pages/2_📈_Historical_Analysis.py`) - Long-term trend analysis
4. **Correlation Analysis** (`pages/3_🔗_Correlation_Analysis.py`) - Relationship analysis between indicators
5. **Inflation Calculator** (`pages/4_🧮_Inflation_Calculator.py`) - Purchasing power and inflation calculations
6. **Data Export** (`pages/5_📋_Data_Export.py`) - Data export functionality

## Key Components

### Utility Modules

#### DataFetcher (`utils/data_fetcher.py`)
- **Purpose**: Centralized data retrieval from external APIs
- **APIs**: FRED API for CPI and M2 money supply, CoinGecko API for Bitcoin data
- **Caching**: 5-minute TTL for API responses
- **Error Handling**: Comprehensive error handling with user-friendly messages

#### InflationCalculator (`utils/calculations.py`)
- **Purpose**: Core inflation calculations and analysis
- **Functions**: Year-over-year inflation, money supply growth, purchasing power calculations
- **Data Processing**: Pandas-based calculations with error handling

#### ChartGenerator (`utils/charts.py`)
- **Purpose**: Creates interactive visualizations using Plotly
- **Chart Types**: Line charts, subplots, correlation matrices
- **Styling**: Consistent color palette and responsive design

### Data Management
- **Caching Strategy**: Two-tier caching with resource caching for utility classes and data caching for API responses
- **Data Sources**: 
  - FRED API for official economic data (CPI, M2 money supply)
  - CoinGecko API for cryptocurrency data
- **Data Processing**: Real-time data transformation and calculation

## Data Flow

1. **User Interaction**: User selects parameters via Streamlit sidebar controls
2. **Data Fetching**: DataFetcher retrieves data from cached sources or APIs
3. **Processing**: InflationCalculator performs calculations on raw data
4. **Visualization**: ChartGenerator creates interactive charts
5. **Display**: Processed data and visualizations rendered in Streamlit interface

## External Dependencies

### APIs
- **FRED API**: Federal Reserve Economic Data for CPI and M2 money supply
- **CoinGecko API**: Cryptocurrency price data for Bitcoin

### Python Libraries
- **Core**: `streamlit`, `pandas`, `numpy`
- **Visualization**: `plotly`, `seaborn`
- **API Clients**: `fredapi`, `requests`
- **Statistics**: `scipy.stats`
- **Environment**: `os` for environment variable management

### Environment Variables
- `FRED_API_KEY`: Required for accessing Federal Reserve Economic Data

## Deployment Strategy

### Streamlit Cloud Deployment
- **Framework**: Native Streamlit deployment
- **Configuration**: `st.set_page_config()` for page settings
- **Caching**: Built-in Streamlit caching for performance optimization
- **Resource Management**: Cached utility classes to minimize initialization overhead

### Performance Optimizations
- **Data Caching**: 5-minute TTL for API responses
- **Resource Caching**: Utility classes cached across sessions
- **Lazy Loading**: Data fetched only when needed
- **Error Recovery**: Graceful handling of API failures

### Security Considerations
- **API Keys**: Environment variable management for sensitive credentials
- **Rate Limiting**: Built-in caching to reduce API calls
- **Error Handling**: Comprehensive error handling to prevent crashes

The application is designed to be easily deployable on Streamlit Cloud or similar platforms, with minimal configuration required beyond setting the FRED API key environment variable.