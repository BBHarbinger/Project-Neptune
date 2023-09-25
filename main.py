# File name: main.py
# Description: Main script to run the application
# Author: Felix Yuzhou Sun
# Verson 0.0.1

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from backend.visualization.chart_primary_lw import chart_init
from backend.data.fetch import StockDatabaseManager

# lightweight_charts version
"""

ATTENTION:      Avoid using inter-day, weekly, and monthly time series for testing
                The alpha vantage API only allows 5 calls per minute and 500 calls per day
                
"""

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the app layout
app.layout = html.Div([
    # Input box for stock symbol
    dcc.Input(id='stock-input', value='TSLA', type='text'),
    html.P(id='feedback', style={'color': 'red'})  # This will display error messages or other feedback
])

# Instantiate the class
db_manager = StockDatabaseManager()

@app.callback(
    Output('feedback', 'children'),  # This will update the content of the feedback paragraph
    [Input('stock-input', 'n_submit')],
    [dash.dependencies.State('stock-input', 'value')]
)
def update_graph(n_submit, stock_symbol):
    if n_submit and n_submit > 0:
        # Use the method from the instantiated class to fetch the data
        data = db_manager.fetch_stock_data(stock_symbol=stock_symbol, time_series="daily5y")
        if data is None or data.empty:  # Check if data is empty DataFrame as well
            return "Invalid stock symbol or data unavailable. Please try again."
        else:
            if __name__ == '__main__':
                chart_init(stock_data=data, stock_symbol=stock_symbol)

    return ""

    return ""  # Return empty string if no error


if __name__ == '__main__':
    # Open the browser first
    #webbrowser.open('http://127.0.0.1:8050/', new=2)  # new=2 opens in a new tab if possible
    # Then run the Dash app
    #app.run_server(debug=True, use_reloader=False)
    chart_init(db_manager, stock_symbol="TSLA")
