import sys
import webbrowser
import os
from datetime import datetime
import requests
import pandas as pd
import plotly.express as px

def get_user_inputs():
    print("=== Stock Data Visualization Tool ===")
    
    # 1. API Key
    api_key = input("Enter your Alpha Vantage API Key (or type 'demo' for IBM test): ").strip()
    if not api_key:
        api_key = "demo"
        print("Using 'demo' key. Note: Demo mode only supports symbol 'IBM'.")

    # 2. Stock Symbol
    symbol = input("Enter the stock symbol (e.g., AAPL, MSFT, IBM): ").strip().upper()

    # 3. Time Series Function
    print("\nSelect Time Series Function:")
    print("1. TIME_SERIES_DAILY")
    print("2. TIME_SERIES_WEEKLY")
    print("3. TIME_SERIES_MONTHLY")
    choice = input("Enter choice (1-3, default 1): ").strip()
    
    func_map = {
        "1": "TIME_SERIES_DAILY",
        "2": "TIME_SERIES_WEEKLY",
        "3": "TIME_SERIES_MONTHLY"
    }
    time_series_func = func_map.get(choice, "TIME_SERIES_DAILY")

    # 4. Chart Type
    print("\nSelect Chart Type:")
    print("1. Line Chart")
    print("2. Scatter/Markers Chart")
    chart_choice = input("Enter choice (1-2, default 1): ").strip()
    chart_type = "scatter" if chart_choice == "2" else "line"

    # 5 & 6. Date Range Validation Loop
    while True:
        try:
            start_date_str = input("Enter beginning date (YYYY-MM-DD): ").strip()
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            
            end_date_str = input("Enter end date (YYYY-MM-DD): ").strip()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            if end_date < start_date:
                print("[Error] End date cannot be before the beginning date. Please try again.\n")
                continue
            break
        except ValueError:
            print("[Error] Invalid date format. Please use YYYY-MM-DD format (e.g., 2025-01-01).\n")

    return api_key, symbol, time_series_func, chart_type, start_date, end_date

def fetch_stock_data(api_key, symbol, function_name):
    url = f"https://www.alphavantage.co/query?function={function_name}&symbol={symbol}&apikey={api_key}"
    
    try:
        print(f"\nFetching data from Alpha Vantage for {symbol}...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Check for API error messages or rate limits
        if "Error Message" in data:
            print(f"[API Error]: {data['Error Message']}")
            return None
        if "Information" in data:
            print(f"[API Notice]: {data['Information']}")
            return None
            
        # Find the correct time series key dynamically in the returned JSON
        time_series_key = None
        for key in data.keys():
            if "Time Series" in key:
                time_series_key = key
                break
                
        if not time_series_key:
            print("[Error] Unexpected API response structure. Could not locate time series data.")
            return None
            
        return data[time_series_key]
    
    except requests.exceptions.RequestException as e:
        print(f"[Network Error]: Failed to connect to API. Details: {e}")
        return None
    except Exception as e:
        print(f"[Error]: An unexpected error occurred: {e}")
        return None

def process_and_plot_data(raw_data, symbol, chart_type, start_date, end_date):
    try:
        # Convert raw dictionary to Pandas DataFrame
        df = pd.DataFrame.from_dict(raw_data, orient='index')
        
        # Clean column names (Alpha Vantage uses keys like '1. open', '4. close')
        df = df.rename(columns={
            '1. open': 'Open',
            '2. high': 'High',
            '3. low': 'Low',
            '4. close': 'Close',
            '5. volume': 'Volume',
            '5. adjusted close': 'Adjusted Close',
            '6. volume': 'Volume'
        })
        
        # Convert index to datetime and numeric columns to float
        df.index = pd.to_datetime(df.index)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Sort chronologically
        df = df.sort_index()

        # Filter by user date range
        mask = (df.index >= start_date) & (df.index <= end_date)
        df_filtered = df.loc[mask]

        if df_filtered.empty:
            print("[Warning] No data found within the specified date range.")
            return

        # Generate graph using Plotly
        title = f"{symbol} Stock Price Trend ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})"
        
        if chart_type == "scatter":
            fig = px.scatter(df_filtered, x=df_filtered.index, y='Close', title=title,
                             labels={'x': 'Date', 'Close': 'Closing Price (USD)'},
                             hover_data=['Open', 'High', 'Low', 'Volume'])
        else:
            fig = px.line(df_filtered, x=df_filtered.index, y='Close', title=title,
                          labels={'x': 'Date', 'Close': 'Closing Price (USD)'},
                          hover_data=['Open', 'High', 'Low', 'Volume'])

        fig.update_xaxes(rangeslider_visible=True)

        # Save to a local HTML file and open in default browser
        output_file = "stock_chart.html"
        fig.write_html(output_file)
        
        abs_path = os.path.abspath(output_file)
        print(f"\n[Success] Graph successfully generated!")
        print(f"Opening '{output_file}' in your default web browser...")
        webbrowser.open(f"file://{abs_path}")

    except Exception as e:
        print(f"[Error] Failed to process data or generate graph: {e}")

def main():
    try:
        api_key, symbol, time_series_func, chart_type, start_date, end_date = get_user_inputs()
        raw_data = fetch_stock_data(api_key, symbol, time_series_func)
        
        if raw_data:
            process_and_plot_data(raw_data, symbol, chart_type, start_date, end_date)
            
    except KeyboardInterrupt:
        print("\n\nProgram terminated by user. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()