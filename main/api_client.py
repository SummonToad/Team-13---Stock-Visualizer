"""Talks to the Alpha Vantage API."""
import requests
import time
import config


class APIError(Exception):
    """Raised for any problem getting data from the API."""


def _request(symbol, function, outputsize=None):
    params = {"function": function, "symbol": symbol, "apikey": config.API_KEY}
    if outputsize:
        params["outputsize"] = outputsize
    try:
        response = requests.get(config.BASE_URL, params=params, timeout=config.REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        raise APIError("Could not connect. Check your internet connection.")
    except requests.exceptions.Timeout:
        raise APIError("The request timed out. Try again.")
    except (requests.exceptions.RequestException, ValueError) as err:
        raise APIError(f"Request failed: {err}")


def _get(symbol, function, outputsize):
    """Make a request, waiting and retrying once if the 1-per-second limit is hit."""
    data = _request(symbol, function, outputsize)
    if "per second" in str(data.get("Information", "")):
        time.sleep(1.5)
        data = _request(symbol, function, outputsize)
    return data


def fetch_stock_data(symbol, function):
    """Return the raw JSON dict for the symbol and time series function."""
    if config.API_KEY == "YOUR_API_KEY_HERE":
        raise APIError("No API key set. Add yours to config.py.")

    # Daily data needs outputsize=full to reach back 20 years.
    outputsize = "full" if function == "TIME_SERIES_DAILY" else None
    data = _get(symbol, function, outputsize)

    # Full daily data can be a premium feature; fall back to the last 100 days.
    if outputsize == "full" and "Information" in data:
        print("Full history needs a premium key; using the last 100 days instead.")
        time.sleep(1.5)  # free keys allow 1 request per second
        data = _get(symbol, function, "compact")

    if "Error Message" in data:
        raise APIError(f"Alpha Vantage could not find symbol '{symbol}'.")
    if "Note" in data or "Information" in data:
        raise APIError(data.get("Note") or data.get("Information"))
    return data
