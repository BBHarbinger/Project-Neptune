from main import app
import dash
from dash.dependencies import Input, Output
from data.fetch import fetch_stock_data


@app.callback(
    Output('stock-graph', 'figure'),
    [Input('search-button', 'n_clicks')],
    [dash.dependencies.State('stock-input', 'value')]
)
def update_graph(n_clicks, stock_symbol):
    if not stock_symbol:
        return dash.no_update  # Do not update if no stock symbol provided

    stock_data = fetch_stock_data(stock_symbol, time_series="daily5y")

    # Convert stock_data to a format suitable for Dash
    figure = {
        'data': [
            # Your data format here, for example:
            {'x': stock_data.time, 'y': stock_data.close, 'type': 'line', 'name': stock_symbol},
        ],
        'layout': {
            'title': stock_symbol
        }
    }
    return figure
