"""
File name:      indicators.py
Description:    This file is the tool box for technical indicators
                on the chart.
Author:         Felix Yuzhou Sun
Version:        0.0.1

All the indicators are calculated base on the following dataframe layout:
data.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
"""

import pandas as pd


# The function to calculate simple moving average based on closing price
# Input:    data->DataFrame
def sma20(data):
    sma20_df = pd.DataFrame(columns=['time', 'value'])
    sma20_df.time = data.time
    sma20_df.SMA20 = data.close.rolling(window=20).mean()
    return sma20_df

