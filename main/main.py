
import sys

import user_input
import api_client
import data_processor
import chart_generator


def main():
    print("=== Stock Data Visualizer ===\n")
    symbol = user_input.get_symbol()
    chart_type = user_input.get_chart_type()
    function = user_input.get_time_series_function()
    start_date = user_input.get_start_date()
    end_date = user_input.get_end_date(start_date)

    try:
        raw = api_client.fetch_stock_data(symbol, function)
        df = data_processor.build_dataframe(raw)
        df = data_processor.filter_by_date(df, start_date, end_date)
    except (api_client.APIError, data_processor.DataError) as err:
        print(f"\nError: {err}")
        sys.exit(1)

    chart_generator.create_chart(df, symbol, chart_type, function, start_date, end_date)


if __name__ == "__main__":
    main()
