"""Prompts the user for input and validates it."""
from datetime import datetime

CHART_TYPES = {"1": "line", "2": "bar"}

TIME_SERIES_FUNCTIONS = {
    "1": "TIME_SERIES_DAILY",
    "2": "TIME_SERIES_WEEKLY",
    "3": "TIME_SERIES_MONTHLY",
}


def get_symbol():
    """Ask for a stock symbol (letters, optionally with . or -)."""
    while True:
        symbol = input("Enter the stock symbol (e.g. IBM, AAPL): ").strip().upper()
        cleaned = symbol.replace(".", "").replace("-", "")
        if symbol and cleaned.isalpha() and len(symbol) <= 10:
            return symbol
        print("Invalid symbol. Use letters only (e.g. IBM).\n")


def _choose(title, options):
    """Show a numbered menu and return the chosen value."""
    while True:
        print(f"\n{title}")
        print("-" * len(title))
        for key, value in options.items():
            print(f"{key}. {value}")
        choice = input(f"Enter your choice ({'/'.join(options)}): ").strip()
        if choice in options:
            return options[choice]
        print("Invalid choice, try again.")


def get_chart_type():
    return _choose("Chart Types", CHART_TYPES)


def get_time_series_function():
    return _choose("Select the time series of the chart you want", TIME_SERIES_FUNCTIONS)


def parse_date(text):
    """Return a datetime.date for a YYYY-MM-DD string, or None if invalid."""
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def get_start_date():
    while True:
        date = parse_date(input("\nEnter the start date (YYYY-MM-DD): "))
        if date:
            return date
        print("Invalid date. Use the format YYYY-MM-DD.")


def get_end_date(start_date):
    while True:
        date = parse_date(input("Enter the end date (YYYY-MM-DD): "))
        if not date:
            print("Invalid date. Use the format YYYY-MM-DD.")
        elif date < start_date:
            print("The end date cannot be before the start date.")
        else:
            return date
