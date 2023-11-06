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
                     (symbol TEXT, time TEXT, open REAL, high REAL, low REAL, close REAL, volume INTEGER, data_type TEXT, 
                     PRIMARY KEY(symbol, time, data_type))''')
        conn.commit()
        conn.close()

    def store_data(self, symbol: str, data: pd.DataFrame, data_type: str) -> None:
        """
        Store the fetched stock data in the SQLite database with an additional column for data type.

        :param symbol: Stock symbol.
        :param data: Fetched stock data.
        :param data_type: Type of data ("daily" or "intraday").
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        for index, row in data.iterrows():
            formatted_time = row['time'].strftime('%Y-%m-%d %H:%M:%S')
            c.execute('''INSERT OR IGNORE INTO stock_data (symbol, time, open, high, low, close, volume, data_type) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (symbol, formatted_time, row['open'], row['high'], row['low'], row['close'], row['volume'], data_type))
        conn.commit()
        conn.close()

    def fetch_daily_data(self, stock_symbol: str, period: str = "1y") -> pd.DataFrame or None:
        """
        Fetch daily stock data using yfinance.

        :param stock_symbol: Stock symbol.
        :param period: Period of the history data (e.g., "1y", "5y", "max").
        :return: Daily stock data as a DataFrame.
        """
        try:
            data = yf.download(stock_symbol, period=period, progress=False)
            data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
            data = data.reset_index()
            data.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            data['time'] = pd.to_datetime(data['time'])

            # Store the data in the database with 'daily' as data_type
            self.store_data(stock_symbol, data, "daily")

            return data

        except Exception as e:
            logger.error(f"Error downloading daily data: {e}")
            return None

    def fetch_intraday_data(self, stock_symbol: str, interval: str = "5min") -> pd.DataFrame:
        """
        Fetch intraday stock data using Alpha Vantage.

        :param stock_symbol: Stock symbol.
        :param interval: Time interval for intraday data (e.g., "5min", "15min").
        :return: Intraday stock data as a DataFrame.
        """
        base_url = "https://www.alphavantage.co/query?"
        endpoint = f"{base_url}function=TIME_SERIES_INTRADAY&symbol={stock_symbol}&interval={interval}&apikey={self.api_key}"

        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            response_data = response.json()

            if "Error Message" in response_data:
                logger.error(f"Error: {response_data['Error Message']}")
                return None

            data = pd.DataFrame(response_data['Time Series (' + interval + ')']).T
            data = data[['1. open', '2. high', '3. low', '4. close', '5. volume']]
            data.columns = ['open', 'high', 'low', 'close', 'volume']
            data = data.reset_index()
            data.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
            data['time'] = pd.to_datetime(data['time'])

            # Store the data in the database with 'intraday' as data_type
            self.store_data(stock_symbol, data, "intraday")

            return data

        except requests.exceptions.HTTPError as errh:
            logger.error(f"HTTP Error: {errh}")
        except KeyError:
            logger.error(f"Possible invalid stock symbol: {stock_symbol} or unexpected response format")
        except Exception as err:
            logger.error(f"Error occurred: {err}")

        return None

    def is_data_up_to_date(self, symbol: str, data_type: str, latest_time: datetime) -> bool:
        """
        Check if the local database has the latest stock data for the specified data type.

        :param symbol: Stock symbol.
        :param data_type: Type of data ("daily" or "intraday").
        :param latest_time: The latest time to check against.
        :return: Boolean indicating if the local data is up to date.
        """
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        # Include the data_type in the WHERE clause to check the latest time for the specific type of data
        c.execute(f"SELECT MAX(time) FROM stock_data WHERE symbol = ? AND data_type = ?", (symbol, data_type))
        max_time = c.fetchone()[0]
        conn.close()
        if max_time is not None:
            max_time = datetime.strptime(max_time, '%Y-%m-%d %H:%M:%S')
            return max_time >= latest_time
        return False


""""
# Example usage
alpha_vantage_key = API_KEY
try:
    stock_data = fetch_stock_data("MSFT", time_series="weekly", alpha_vantage_api_key=alpha_vantage_key)
    print(stock_data)
except ValueError as e:
    print(e)
"""
