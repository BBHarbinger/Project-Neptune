import tkinter as tk
import mplfinance as mpf

def update_chart():
    stock_symbol = stock_entry.get()
    time_series = time_series_var.get()

    data = fetch_stock_data(stock_symbol, time_series)
    if data is not None:
        mpf.plot(data, type='candle', style='charles', volume=True, figscale=1.25)
