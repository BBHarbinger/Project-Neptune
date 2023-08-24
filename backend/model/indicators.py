"""
File name:      indicators.py
Description:    This file is the tool box for technical indicators
                on the chart.
Author:         Felix Yuzhou Sun
Version:        0.0.1

All the indicators are calculated base on the following dataframe layout:
data.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
"""
#import numpy as np
import pandas as pd
#import pandas_ta as ta

"""
SMAs: Simple Moving Averages
"""


# The function to calculate nd simple moving average based on closing price
# Input:    data->DataFrame
#           n->int
# Output:   sma_df->DataFrame
def sma(n):
    def sma_nd(data):
        sma_df = pd.DataFrame(columns=['time', 'value'])
        sma_df.time = data.time
        sma_df.SMA = data.close.rolling(window=n).mean()
        return sma_df

    return sma_nd


"""
EMAs: Exponential Moving Averages
"""


# The function to calculate nd exponential moving average based on closing price
# Input:    data->DataFrame
#           n->int
# Output:   ema_df->DataFrame
def ema(n):
    def ema_nd(data):
        ema_df = pd.DataFrame(columns=['time', 'value'])
        ema_df.time = data.time
        ema_df.EMA = data.close.ewm(span=n, adjust=False).mean()
        return ema_df

    return ema_nd


"""
Golden Cross and Death Cross
"""


# use the existing function (smas) and (emas) to calculate the golden cross and death cross
# Input:    data->DataFrame
#           short_term->int
#           long_term->int
#           ma_function->Function
# Output:   cross_df->List<DataFrame>
def cross(data, short_term, long_term, ma_function):
    # Calculate the moving averages
    short_term_ma = ma_function(short_term)(data)
    long_term_ma = ma_function(long_term)(data)

    # Create a new DataFrame based on the original data
    cross_list = data.copy()

    # Identify where the short-term MA is above or below the long-term MA
    cross_list['GC'] = (short_term_ma > long_term_ma) & (short_term_ma.shift(1) <= long_term_ma.shift(1))
    cross_list['DC'] = (short_term_ma < long_term_ma) & (short_term_ma.shift(1) >= long_term_ma.shift(1))

    return cross_list.dropna()



