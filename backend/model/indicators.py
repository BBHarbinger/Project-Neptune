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

"""
SMAs: Simple Moving Averages
"""


# Short term SMAs

# The function to calculate 5d simple moving average based on closing price
# Input:    data->DataFrame
# Output:   sma10_df->DataFrame
def sma5(data):
    sma5_df = pd.DataFrame(columns=['time', 'value'])
    sma5_df.time = data.time
    sma5_df.SMA5 = data.close.rolling(window=5).mean()
    return sma5_df


# The function to calculate 10d simple moving average based on closing price
# Input:    data->DataFrame
# Output:   sma10_df->DataFrame
def sma10(data):
    sma10_df = pd.DataFrame(columns=['time', 'value'])
    sma10_df.time = data.time
    sma10_df.SMA10 = data.close.rolling(window=10).mean()
    return sma10_df


# Intermediate-term SMAs

# The function to calculate 20d simple moving average based on closing price
# Input:    data->DataFrame
# Output:   sma20_df->DataFrame
def sma20(data):
    sma20_df = pd.DataFrame(columns=['time', 'value'])
    sma20_df.time = data.time
    sma20_df.SMA20 = data.close.rolling(window=20).mean()
    return sma20_df


# The function to calculate 30d simple moving average based on closing price
# Input:    data->DataFrame
# Output:   sma20_df->DataFrame
def sma30(data):
    sma30_df = pd.DataFrame(columns=['time', 'value'])
    sma30_df.time = data.time
    sma30_df.SMA30 = data.close.rolling(window=30).mean()
    return sma30_df


# Long term SMAs

# The function to calculate 50d simple moving average based on closing price
# Input:    data->DataFrame
# Output:   sma50_df->DataFrame
def sma50(data):
    sma50_df = pd.DataFrame(columns=['time', 'value'])
    sma50_df.time = data.time
    sma50_df.SMA50 = data.close.rolling(window=50).mean()
    return sma50_df


# The function to calculate 100d simple moving average based on closing price
# Input:    data->DataFrame
# Output:   sma100_df->DataFrame
def sma100(data):
    sma100_df = pd.DataFrame(columns=['time', 'value'])
    sma100_df.time = data.time
    sma100_df.SMA100 = data.close.rolling(window=100).mean()
    return sma100_df


# The function to calculate 200d simple moving average based on closing price
# Input:    data->DataFrame
# Output:   sma200_df->DataFrame
def sma200(data):
    sma200_df = pd.DataFrame(columns=['time', 'value'])
    sma200_df.time = data.time
    sma200_df.SMA200 = data.close.rolling(window=200).mean()
    return sma200_df


"""
EMAs: Exponential Moving Averages
"""


# Short term EMAs

# The function to calculate 5d exponential moving average based on closing price
# Input:    data->DataFrame
# Output:   ema5_df->DataFrame
def ema5(data):
    ema5_df = pd.DataFrame(columns=['time', 'value'])
    ema5_df.time = data.time
    ema5_df.EMA5 = data.close.ewm(span=5, adjust=False).mean()
    return ema5_df


# The function to calculate 9d exponential moving average based on closing price
# Input:    data->DataFrame
# Output:   ema9_df->DataFrame
def ema9(data):
    ema9_df = pd.DataFrame(columns=['time', 'value'])
    ema9_df.time = data.time
    ema9_df.EMA9 = data.close.ewm(span=9, adjust=False).mean()
    return ema9_df


# The function to calculate 12d exponential moving average based on closing price
# Input:    data->DataFrame
# Output:   ema12_df->DataFrame
def ema12(data):
    ema12_df = pd.DataFrame(columns=['time', 'value'])
    ema12_df.time = data.time
    ema12_df.EMA12 = data.close.ewm(span=12, adjust=False).mean()
    return ema12_df


# Intermediate-term EMAs

# The function to calculate 20d exponential moving average based on closing price
# Input:    data->DataFrame
# Output:   ema20_df->DataFrame
def ema20(data):
    ema20_df = pd.DataFrame(columns=['time', 'value'])
    ema20_df.time = data.time
    ema20_df.EMA20 = data.close.ewm(span=20, adjust=False).mean()
    return ema20_df


# The function to calculate 26d exponential moving average based on closing price
# Input:    data->DataFrame
# Output:   ema26_df->DataFrame
def ema26(data):
    ema26_df = pd.DataFrame(columns=['time', 'value'])
    ema26_df.time = data.time
    ema26_df.EMA26 = data.close.ewm(span=26, adjust=False).mean()
    return ema26_df


# Long term EMAs

# The function to calculate 50d exponential moving average based on closing price
# Input:    data->DataFrame
# Output:   ema50_df->DataFrame
def ema50(data):
    ema50_df = pd.DataFrame(columns=['time', 'value'])
    ema50_df.time = data.time
    ema50_df.EMA50 = data.close.ewm(span=50, adjust=False).mean()
    return ema50_df


# The function to calculate 100d exponential moving average based on closing price
# Input:    data->DataFrame
# Output:   ema100_df->DataFrame
def ema100(data):
    ema100_df = pd.DataFrame(columns=['time', 'value'])
    ema100_df.time = data.time
    ema100_df.EMA100 = data.close.ewm(span=100, adjust=False).mean()
    return ema100_df


# The function to calculate 200d exponential moving average based on closing price
# Input:    data->DataFrame
# Output:   ema200_df->DataFrame
def ema200(data):
    ema200_df = pd.DataFrame(columns=['time', 'value'])
    ema200_df.time = data.time
    ema200_df.EMA200 = data.close.ewm(span=200, adjust=False).mean()
    return ema200_df


"""
Golden Cross and Death Cross
"""


# The function to calculate the golden cross and death cross
# Input:    short_term_ma->DataFrame
#           long_term_ma->DataFrame
# Output:   cross_df->List<DataFrame>
#           (fist element is golden cross, second element is death cross)
def calculate_crosses(short_term_ma, long_term_ma):
    golden_crosses = pd.DataFrame(columns=['time', 'value'])
    death_crosses = pd.DataFrame(columns=['time', 'value'])

    for i in range(1, len(short_term_ma)):
        current_short = short_term_ma.iloc[i]['value']
        current_long = long_term_ma.iloc[i]['value']

        prev_short = short_term_ma.iloc[i - 1]['value']
        prev_long = long_term_ma.iloc[i - 1]['value']

        # Check for golden cross
        if current_short > current_long and prev_short < prev_long:
            golden_crosses = golden_crosses.append({'time': short_term_ma.iloc[i]['time'],
                                                    'value': current_short},
                                                   ignore_index=True)

        # Check for death cross
        if current_short < current_long and prev_short > prev_long:
            death_crosses = death_crosses.append({'time': short_term_ma.iloc[i]['time'],
                                                  'value': current_short},
                                                 ignore_index=True)

    return [golden_crosses, death_crosses]

