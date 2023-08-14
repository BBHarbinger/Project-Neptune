# Name: fetch.py
# This file is used to fetch data from the database
# The api we use here is from https://www.alphavantage.co/
# and yahoo finance
# API KEY for alpha vantage: M8WLSWBJFH1HZ19L
# Author: Felix Yuzhou Sun
# Version: 0.0.1
# The function to fetch data of a specific stock from the API

import yfinance as yf

# This is the APO key we use to fetch data from the API
API_KEY = "M8WLSWBJFH1HZ19L"


# This is the exception class that will be raised when the time series is invalid
class InvalidTimeSeriesError(Exception):
    pass


# This function is used to fetch data from the API
def fetch_stock_data(stock_symbol, time_series, period="max"):
    stock = yf.Ticker(stock_symbol)

    try:
        if time_series == "daily":
            data = stock.history(period=period)
        elif time_series == "weekly":
            data = stock.history(period=period, interval="1wk")
        elif time_series == "hourly":
            data = stock.history(period=period, interval="1h")
        elif time_series == "monthly":
            data = stock.history(period=period, interval="1mo")
        elif time_series == "20min":  # our custom interval
            data = stock.history(period=period, interval="5m")  # fetch 5-minute data
            data = data.resample('20T').mean()  # resample to 20 minutes, taking the mean value

        else:
            raise InvalidTimeSeriesError(f"'{time_series}' is not a valid time series selection.")

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return data


# Usage example:
data = fetch_stock_data("AAPL", "daily", period="1y")
print(data)
