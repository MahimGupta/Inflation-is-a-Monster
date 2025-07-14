import streamlit as st
import pandas as pd
import io
import json
from datetime import datetime, timedelta
from utils.data_fetcher import DataFetcher
from utils.calculations import InflationCalculator

st.set_page_config(page_title="Data Export - Inflation Monster", page_icon="📋", layout="wide")

@st.cache_resource
def get_data_fetcher():
    return DataFetcher()

@st.cache_resource
def get_calculator():
    return InflationCalculator()

def main():
    st.title("📋 Data Export")
    st.markdown("Export economic data and analysis results in various formats")
    
    # Initialize components
    data_fetcher = get_data_fetcher()
    calculator = get_calculator()
    
    # Sidebar controls
    st.sidebar.header("Export Controls")
    
    # Data selection
    data_types = st.sidebar.multiselect(
        "Select Data Types",
        ["CPI", "M2 Money Supply", "Bitcoin", "Calculated Metrics"],
        default=["CPI", "Bitcoin"]
    )
    
    # Date range
    date_range = st.sidebar.selectbox(
        "Date Range",
        ["1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years", "All Available"],
        index=3
    )
    
    # Export format
    export_format = st.sidebar.selectbox(
        "Export Format",
        ["CSV", "Excel", "JSON", "PDF Report"],
        index=0
    )
    
    # Convert date range to days
    range_mapping = {
        "1 Month": 30,
        "3 Months": 90,
        "6 Months": 180,
        "1 Year": 365,
        "2 Years": 730,
        "5 Years": 1825,
        "All Available": None
    }
    days = range_mapping[date_range]
    
    # Main content
    st.header("📊 Data Preview")
    
    try:
        # Fetch data based on selection
        with st.spinner("Loading data for export..."):
            export_data = {}
            
            if "CPI" in data_types:
                cpi_data = data_fetcher.get_cpi_data(days=days)
                if not cpi_data.empty:
                    export_data["CPI"] = cpi_data
            
            if "M2 Money Supply" in data_types:
                m2_data = data_fetcher.get_m2_data(days=days)
                if not m2_data.empty:
                    export_data["M2_Money_Supply"] = m2_data
            
            if "Bitcoin" in data_types:
                bitcoin_data = data_fetcher.get_bitcoin_data(days=days)
                if not bitcoin_data.empty:
                    export_data["Bitcoin"] = bitcoin_data
            
            if "Calculated Metrics" in data_types and "CPI" in data_types:
                if "CPI" in export_data:
                    cpi_data = export_data["CPI"]
                    
                    # Calculate various metrics
                    metrics_data = calculate_metrics(cpi_data, calculator)
                    export_data["Calculated_Metrics"] = metrics_data
        
        # Display data preview
        if export_data:
            tab_names = list(export_data.keys())
            tabs = st.tabs(tab_names)
            
            for i, (data_name, data) in enumerate(export_data.items()):
                with tabs[i]:
                    st.subheader(f"{data_name} Data")
                    
                    if isinstance(data, pd.DataFrame):
                        st.dataframe(data.head(100), use_container_width=True)
                        st.info(f"Total records: {len(data)}")
                    elif isinstance(data, dict):
                        st.json(data)
                    else:
                        st.write(data)
        
        # Export section
        st.header("📁 Export Options")
        
        if export_data:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Quick Export")
                
                # Generate export based on format
                if export_format == "CSV":
                    if st.button("Generate CSV Files", type="primary"):
                        csv_files = generate_csv_files(export_data)
                        st.session_state.csv_files = csv_files
                        st.success("CSV files generated successfully!")
                
                elif export_format == "Excel":
                    if st.button("Generate Excel File", type="primary"):
                        excel_file = generate_excel_file(export_data)
                        st.session_state.excel_file = excel_file
                        st.success("Excel file generated successfully!")
                
                elif export_format == "JSON":
                    if st.button("Generate JSON File", type="primary"):
                        json_file = generate_json_file(export_data)
                        st.session_state.json_file = json_file
                        st.success("JSON file generated successfully!")
                
                elif export_format == "PDF Report":
                    if st.button("Generate PDF Report", type="primary"):
                        st.info("PDF report generation would require additional libraries. For now, use CSV/Excel export.")
            
            with col2:
                st.subheader("Custom Export")
                
                # Custom date range
                if export_data:
                    sample_data = list(export_data.values())[0]
                    if isinstance(sample_data, pd.DataFrame) and not sample_data.empty:
                        min_date = sample_data.index.min().date()
                        max_date = sample_data.index.max().date()
                        
                        custom_start = st.date_input(
                            "Custom Start Date",
                            value=min_date,
                            min_value=min_date,
                            max_value=max_date
                        )
                        
                        custom_end = st.date_input(
                            "Custom End Date",
                            value=max_date,
                            min_value=min_date,
                            max_value=max_date
                        )
                        
                        if st.button("Export Custom Range"):
                            custom_export_data = filter_data_by_date(
                                export_data, custom_start, custom_end
                            )
                            
                            if export_format == "CSV":
                                csv_files = generate_csv_files(custom_export_data)
                                st.session_state.csv_files = csv_files
                            elif export_format == "Excel":
                                excel_file = generate_excel_file(custom_export_data)
                                st.session_state.excel_file = excel_file
                            elif export_format == "JSON":
                                json_file = generate_json_file(custom_export_data)
                                st.session_state.json_file = json_file
                            
                            st.success(f"Custom range export generated!")
        
        # Download section
        st.header("⬇️ Download Files")
        
        if export_format == "CSV" and hasattr(st.session_state, 'csv_files'):
            st.subheader("CSV Files")
            for filename, file_data in st.session_state.csv_files.items():
                st.download_button(
                    label=f"Download {filename}",
                    data=file_data,
                    file_name=filename,
                    mime="text/csv"
                )
        
        elif export_format == "Excel" and hasattr(st.session_state, 'excel_file'):
            st.download_button(
                label="Download Excel File",
                data=st.session_state.excel_file,
                file_name=f"inflation_monster_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        elif export_format == "JSON" and hasattr(st.session_state, 'json_file'):
            st.download_button(
                label="Download JSON File",
                data=st.session_state.json_file,
                file_name=f"inflation_monster_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Data summary
        st.header("📋 Export Summary")
        
        if export_data:
            summary_data = []
            for data_name, data in export_data.items():
                if isinstance(data, pd.DataFrame):
                    summary_data.append({
                        "Dataset": data_name,
                        "Records": len(data),
                        "Date Range": f"{data.index.min().strftime('%Y-%m-%d')} to {data.index.max().strftime('%Y-%m-%d')}",
                        "Columns": len(data.columns)
                    })
                elif isinstance(data, dict):
                    summary_data.append({
                        "Dataset": data_name,
                        "Records": len(data),
                        "Date Range": "N/A",
                        "Columns": "N/A"
                    })
            
            if summary_data:
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True)
        
        # Data attribution
        st.header("📚 Data Attribution")
        
        attribution_info = {
            "CPI Data": "Federal Reserve Economic Data (FRED) - Consumer Price Index for All Urban Consumers",
            "M2 Money Supply": "Federal Reserve Economic Data (FRED) - M2 Money Stock",
            "Bitcoin Data": "CoinGecko API - Bitcoin Price Data",
            "Calculated Metrics": "Derived from CPI data using standard economic formulas"
        }
        
        for source, description in attribution_info.items():
            if any(source.replace(" Data", "").replace(" ", "_").lower() in key.lower() for key in export_data.keys()):
                st.write(f"**{source}**: {description}")
        
        st.markdown("---")
        st.markdown("**Note**: Please ensure proper attribution when using this data in your analysis or publications.")
    
    except Exception as e:
        st.error(f"Error in data export: {str(e)}")
        st.info("Please check your data sources and try again.")

def calculate_metrics(cpi_data, calculator):
    """Calculate various metrics from CPI data"""
    metrics = {}
    
    # Monthly inflation rates
    monthly_inflation = cpi_data['value'].pct_change() * 100
    metrics['Monthly_Inflation_Rate'] = monthly_inflation.dropna()
    
    # Year-over-year inflation
    yoy_inflation = cpi_data['value'].pct_change(periods=12) * 100
    metrics['YoY_Inflation_Rate'] = yoy_inflation.dropna()
    
    # Rolling averages
    metrics['3_Month_MA'] = cpi_data['value'].rolling(window=3).mean()
    metrics['6_Month_MA'] = cpi_data['value'].rolling(window=6).mean()
    metrics['12_Month_MA'] = cpi_data['value'].rolling(window=12).mean()
    
    # Volatility metrics
    metrics['Monthly_Volatility'] = monthly_inflation.rolling(window=12).std()
    
    # Create DataFrame
    metrics_df = pd.DataFrame(metrics)
    return metrics_df

def generate_csv_files(export_data):
    """Generate CSV files for each dataset"""
    csv_files = {}
    
    for data_name, data in export_data.items():
        if isinstance(data, pd.DataFrame):
            csv_buffer = io.StringIO()
            data.to_csv(csv_buffer, index=True)
            csv_files[f"{data_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"] = csv_buffer.getvalue()
    
    return csv_files

def generate_excel_file(export_data):
    """Generate Excel file with multiple sheets"""
    excel_buffer = io.BytesIO()
    
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        for data_name, data in export_data.items():
            if isinstance(data, pd.DataFrame):
                # Limit sheet name length
                sheet_name = data_name[:31]
                data.to_excel(writer, sheet_name=sheet_name, index=True)
    
    excel_buffer.seek(0)
    return excel_buffer.getvalue()

def generate_json_file(export_data):
    """Generate JSON file with all data"""
    json_data = {}
    
    for data_name, data in export_data.items():
        if isinstance(data, pd.DataFrame):
            json_data[data_name] = data.to_dict(orient='index')
        elif isinstance(data, dict):
            json_data[data_name] = data
    
    # Add metadata
    json_data['metadata'] = {
        'export_date': datetime.now().isoformat(),
        'source': 'Inflation Monster',
        'datasets': list(export_data.keys())
    }
    
    return json.dumps(json_data, indent=2, default=str)

def filter_data_by_date(export_data, start_date, end_date):
    """Filter data by custom date range"""
    filtered_data = {}
    
    for data_name, data in export_data.items():
        if isinstance(data, pd.DataFrame):
            mask = (data.index.date >= start_date) & (data.index.date <= end_date)
            filtered_data[data_name] = data[mask]
        else:
            filtered_data[data_name] = data
    
    return filtered_data

if __name__ == "__main__":
    main()
