"""
File name:      chart_primary_lw.py
Description:    This file would define how the primary chart looks and behaves
                incorporating lightweight-charts package
                (https://github.com/louisnw01/lightweight-charts-python.git)
Author:         Felix Yuzhou Sun
Version:        0.0.1

p.s:
# In cmd, use [pip install lightweight-charts]
# You can also manually download the package from github

"""
import pandas as pd
from lightweight_charts import Chart
from data.fetch import fetch_stock_data, API_KEY


def chart_init(stock_symbol="AAPL", time_series="daily5y", alpha_vantage_api_key=None):
    chart = Chart()
    alpha_vantage_key = API_KEY
    chart = Chart()

    # Initialize the chart layout
    chart.grid(vert_enabled=True, horz_enabled=True)

    chart.topbar.textbox('symbol:', stock_symbol)

    chart.layout(background_color='#131722', font_family='Trebuchet MS', font_size=20)

    chart.candle_style(up_color='#37ad8a', down_color='#991c3f',
                       border_up_color='#37ad8a', border_down_color='#991c3f',
                       wick_up_color='#37ad8a', wick_down_color='#991c3f')

    chart.volume_config(up_color='#49876b', down_color='#f5678f')

    # chart.watermark(time_series, color='rgba(180, 180, 240, 0.7)')

    chart.crosshair(mode='normal', vert_color='#ffffff', vert_style='dotted',
                    horz_color='#ffffff', horz_style='dotted')

    # chart.title(stock_symbol)
    chart.legend(visible=True, font_family='Trebuchet MS', ohlc=True, percent=True, font_size=15)

    # Fetch data
    stock_data = fetch_stock_data(stock_symbol, time_series=time_series,
                                  alpha_vantage_api_key=alpha_vantage_key)
    # Load data
    chart.set(stock_data)

    # Styling settings
    # Reference: https://levelup.gitconnected.com/replicating-tradingview-chart-in-python-8bb6ff00bb4e
    chart.price_line(title=stock_symbol)

    # Add simple moving average lines 20 and 50
    sma20 = pd.DataFrame(columns=['time', 'SMA20'])
    sma20.time = stock_data.time
    sma20.SMA20 = stock_data.close.rolling(window=20).mean()
    sma20_line = chart.create_line(name='SMA20', color='#ffeb3b', width=1, price_label=True)
    sma20_line.set(sma20.dropna())

    sma50 = pd.DataFrame(columns=['time', 'SMA50'])
    sma50.time = stock_data.time
    sma50.SMA50 = stock_data.close.rolling(window=50).mean()
    sma50_line = chart.create_line(name='SMA50', color='#26c6da', width=1, price_label=True)
    sma50_line.set(sma50.dropna())

    chart.show(block=True)
