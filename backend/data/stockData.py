"""
Name:           stockData.py
Description:    This the class that 'encapsulates' the stock data,
                Although Python does not have the concept of encapsulation
Author:         Felix Yuzhou Sun
Version:        0.0.1
"""


class StockData:

    # Constructor for the StockData class
    # Inputs:   _stock_symbol->String:              the stock symbol of the stock
    #           history_data->HashMap<Dataframe>:   the history data fetched by the fetch function,
    #                                               the key is the time series, the value is the dataframe
    def __init__(self, stock_symbol,
                 history_data,
                 time_series="daily5y"):
        self._stock_symbol = stock_symbol
        # initialize the history data dictionary
        self.history_data = {time_series: history_data}
        # initialize the indicators dictionary
        self.indicators = {}

    # The function to add a new time series to the history data
    # Inputs:   new_time_series->String:    the new time series to be added
    #           new_data->Dataframe:        the new data to be added
    def add_new_time_series(self, new_time_series, new_data):
        self.history_data[new_time_series] = new_data

    # The function to update the existing time series
    # Inputs:   updated_data->Dataframe:    the updated data
    #           time_series->String:        the time series to be updated
    def update_data(self, time_series, updated_data):
        self.history_data[time_series] = updated_data

    # The function to pass in a function to calculate the indicators for
    # a specific time series
    # Inputs:   time_series->String:            the time series to calculate the indicators' values
    #           indicator_name->String:         the name of the indicator
    #           indicator_function->Function:   the function to calculate the indicators
    #                                           for the time series

    def calculate_indicators(self, time_series, indicator_name, indicator_function):
        self.indicators[indicator_name] = indicator_function(self.history_data[time_series])

    # The function to get a specific indicator's value
    # Inputs:   indicator_name->String:     the name of the indicator
    # Outputs:  indicator_value->Dataframe: the value of the indicator
    def get_indicator_value(self, indicator_name):
        # if the indicator exists, return the value
        if indicator_name in self.indicators:
            return self.indicators[indicator_name]
        # if the indicator does not exist, return None
        else:
            return None

