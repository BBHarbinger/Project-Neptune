"""
Name:           fetch.py
Description:    This file is used to fetch data from the database
                The api we use here is from https://www.alphavantage.co/
                and yahoo finance
                [API KEY for alpha vantage: M8WLSWBJFH1HZ19L]
Author:         Felix Yuzhou Sun
Version:        0.0.1
"""

import requests
import yfinance as yf
import pandas as pd

# This is the APO key we may use to fetch data from the alpha vantage API
API_KEY = "M8WLSWBJFH1HZ19L"

"""
This function is used to fetch data from the API
We get daily data from yahoo finance and intraday, weekly, and monthly data from alpha vantage
Input:  stock_symbol: the stock symbol of the stock
        time_series: the target time series of the data
        period: the period of the history data
Output: data: the data fetched from the API
"""


def fetch_stock_data(stock_symbol, time_series="daily100d", alpha_vantage_api_key=None):
    base_url = "https://www.alphavantage.co/query?"

    # Define the endpoints based on the time series
    endpoints = {
        "daily100d": f"{base_url}function=TIME_SERIES_DAILY&symbol={stock_symbol}&apikey={alpha_vantage_api_key}",
        "interday": f"{base_url}function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval=5min&apikey={alpha_vantage_api_key}",
        "monthly": f"{base_url}function=TIME_SERIES_MONTHLY&symbol={stock_symbol}&apikey={alpha_vantage_api_key}",
        "weekly": f"{base_url}function=TIME_SERIES_WEEKLY&symbol={stock_symbol}&apikey={alpha_vantage_api_key}"
    }

    # If the time series is daily (more than 100days), we use the yfinance package to fetch data
    # since the alpha vantage API only allows 100 days of data
    if time_series in ["dailymax", "daily1y", "daily5y", "daily10y", "daily20y"]:
        try:
            if time_series == "dailymax":
                period = "max"
            elif time_series == "daily1y":
                period = "1y"
            elif time_series == "daily5y":
                period = "5y"
            elif time_series == "daily10y":
                period = "10y"
            elif time_series == "daily20y":
                period = "20y"
            else:
                period = "1y"   # Default period is 1 year

            data = yf.download(stock_symbol, period=period, progress=False)
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            data = data.reset_index()
            data.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            return data
        except Exception as e:
            raise ValueError(f"An error occurred while fetching data from Yahoo: {e}")

    try:
        # For other time series, we use the alpha vantage API
        response = requests.get(endpoints[time_series])
        response_data = response.json()
        # Extract the appropriate data depending on the chosen time series
        data_keys = {
            "daily100d": "Time Series (Daily)",
            "interday": "Time Series (5min)",
            "monthly": "Monthly Time Series",
            "weekly": "Weekly Time Series"
        }

        data = pd.DataFrame(response_data[data_keys[time_series]]).T
        data = data[['1. open', '2. high', '3. low', '4. close', '5. volume']]
        data.columns = ['open', 'high', 'low', 'close', 'volume']
        data = data.reset_index()
        data.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        data['time'] = pd.to_datetime(data['time'])

        return data

    except KeyError:
        raise ValueError(f"Stock symbol {stock_symbol} not found or data not available.")
    except Exception as e:
        raise ValueError(f"An error occurred: {e}")


# Example usage
alpha_vantage_key = API_KEY
try:
    stock_data = fetch_stock_data("MSFT", time_series="weekly", alpha_vantage_api_key=alpha_vantage_key)
    print(stock_data)
except ValueError as e:
    print(e)
