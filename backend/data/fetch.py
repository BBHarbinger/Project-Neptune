"""
Name:           fetch.py
Description:    This file is used to fetch data from the database
                The api we use here is from https://www.alphavantage.co/
                and yahoo finance
                [API KEY for alpha vantage: M8WLSWBJFH1HZ19L]
Author:         Felix Yuzhou Sun
Version:        0.0.1
"""

import sqlite3
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime
import logging

# This is the APO key we may use to fetch data from the alpha vantage API
API_KEY = "M8WLSWBJFH1HZ19L"

"""
Name:           fetch_stock_data
Description:    This function is used to fetch data from the API
                We get daily data from yahoo finance and intraday, weekly, 
                and monthly data from alpha vantage
Inputs:         stock_symbol: the stock symbol of the stock
                time_series: the target time series of the data
                period: the period of the history data
Output:         data: the data fetched from the API

ATTENTION:      Avoid using inter-day, weekly, and monthly time series for testing
                The alpha vantage API only allows 5 calls per minute and 500 calls per day

"""
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDatabaseManager:
    def __init__(self, db_name: str = "stock_data.db", api_key: str = "M8WLSWBJFH1HZ19L"):
        """
        Initialize the StockDatabaseManager object and the database.

        :param db_name: Name of the SQLite database file.
        :param api_key: API key for Alpha Vantage.
        """
        self.db_name = db_name
        self.api_key = api_key
        self.initialize_db()

    def initialize_db(self) -> None:
        """
        Initialize the SQLite database with the required table if not already present.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS stock_data 
                     (symbol TEXT, time TEXT, open REAL, high REAL, low REAL, close REAL, volume INTEGER, PRIMARY KEY(symbol, time))''')
        conn.commit()
        conn.close()

    def store_data(self, symbol: str, data: pd.DataFrame) -> None:
        """
        Store the fetched stock data in the SQLite database.

        :param symbol: Stock symbol.
        :param data: Fetched stock data.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        for index, row in data.iterrows():
            formatted_time = row['time'].strftime('%Y-%m-%d %H:%M:%S')
            c.execute('''INSERT OR IGNORE INTO stock_data (symbol, time, open, high, low, close, volume) 
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (symbol, formatted_time, row['open'], row['high'], row['low'], row['close'], row['volume']))
        conn.commit()
        conn.close()

    def fetch_local_data(self, symbol: str, time_series: str) -> pd.DataFrame:
        """
        Fetch the stock data from the local SQLite database.

        :param symbol: Stock symbol.
        :param time_series: Time series of the data.
        :return: Stock data.
        """
        conn = sqlite3.connect(self.db_name)
        data = pd.read_sql_query(f"SELECT * FROM stock_data WHERE symbol = '{symbol}'", conn)
        conn.close()
        data['time'] = pd.to_datetime(data['time'])
        return data

    def is_data_up_to_date(self, symbol: str, latest_time: datetime) -> bool:
        """
        Check if the local database has the latest stock data.

        :param symbol: Stock symbol.
        :param latest_time: The latest time to check against.
        :return: Boolean indicating if the local data is up to date.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute(f"SELECT MAX(time) FROM stock_data WHERE symbol = '{symbol}'")
        max_time = c.fetchone()[0]
        conn.close()
        if max_time is not None:
            max_time = datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')
            return max_time >= latest_time
        return False

    def fetch_stock_data(self, stock_symbol: str, time_series: str = "daily100d", alpha_vantage_api_key: str = None) -> pd.DataFrame:

        # If local data is up to date, fetch from local database
        latest_time = datetime.now()  # Modify it as per your requirement
        if self.is_data_up_to_date(stock_symbol, latest_time):
            return self.fetch_local_data(stock_symbol, time_series)

        # If API key is not provided, use the instance's API key
        if alpha_vantage_api_key is None:
            alpha_vantage_api_key = self.api_key

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
                    period = "1y"  # Default period is 1 year

                data = yf.download(stock_symbol, period=period, progress=False)
                data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
                data = data.reset_index()
                data.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
                return data

            except Exception as e:
                print(f"Error downloading data: {e}")
                return None

        try:
            # For other time series, we use the alpha vantage API
            response = requests.get(endpoints[time_series])
            # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
            response.raise_for_status()
            response_data = response.json()
            # Check if the response contains an error message
            if "Error Message" in response_data:
                print(f"Error: {response_data['Error Message']}")  # Log the error message for debugging
                return None
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


            # Check data integrity before storing
            if data is not None and not data.empty:
                self.store_data(stock_symbol, data)
            return data

        except requests.exceptions.HTTPError as errh:
            logger.error(f"Http Error: {errh}")
        except KeyError:
            logger.error(f"Possible invalid stock symbol: {stock_symbol} or unexpected response format")
        except Exception as err:
            logger.error(f"Error occurred: {err}")

        return None


""""
# Example usage
alpha_vantage_key = API_KEY
try:
    stock_data = fetch_stock_data("MSFT", time_series="weekly", alpha_vantage_api_key=alpha_vantage_key)
    print(stock_data)
except ValueError as e:
    print(e)
"""
