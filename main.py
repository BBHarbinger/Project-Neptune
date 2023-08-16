# File name: main.py
# Description: Main script to run the application
# Author: Felix Yuzhou Sun
# Verson 0.0.1

# 1.Dash version

import pandas as pd
import requests
import numpy as np
from lightweight_charts import Chart
import time
import asyncio
import nest_asyncio

from components.visualization.chart_primary_lw import chart_init
from data.fetch import fetch_stock_data, API_KEY


"""
# Function to open the web page
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# Delayed browser opening
threading.Timer(1, open_browser).start()

if __name__ == '__main__':
    app.run_server(debug=True)

"""

#2. lightweight_charts version
"""

ATTENTION:      Avoid using inter-day, weekly, and monthly time series for testing
                The alpha vantage API only allows 5 calls per minute and 500 calls per day
                
"""
if __name__ == '__main__':
    chart_init()