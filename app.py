import dash
from dash import html, dcc, Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import webbrowser
from dash.dependencies import Input, Output, State
import yfinance as yf
import pandas as pd
from data.fetch import *

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Project Neptune"),
    dcc.Input(id='stock-input', type='text', placeholder='Enter a stock symbol...'),
    dcc.Graph(
        id='stock-graph',
        config={
            'displayModeBar': True,  # Enable the display mode bar
            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],  # Remove lasso and select buttons
            'displaylogo': False,  # Remove the Plotly logo
        }
    ),
    html.Label('Select Time Range:'),
    dcc.Dropdown(
        id='time-range-dropdown',
        options=[
            {'label': '2 Year', 'value': '2y'},
            {'label': '5 Years', 'value': '5y'},
            {'label': '20 Years', 'value': '20y'}
        ],
        value='2y'  # Default value
    ),
    html.Label('Select SMA Periods:'),
    dcc.Checklist(
        id='sma-checklist',
        options=[
            {'label': '30-day SMA', 'value': 'sma_30'},
            {'label': '50-day SMA', 'value': 'sma_50'}
        ],
        value=[]  # Initially, both SMAs are not selected
    )
])

@app.callback(
    Output('stock-graph', 'figure'),
    [Input('stock-input', 'value'),
     Input('time-range-dropdown', 'value'),
     Input('sma-checklist', 'value')]
)
def update_graph(stock_symbol, time_range, sma_periods):
    if not stock_symbol:
        return go.Figure()

    try:
        db_manager = StockDatabaseManager()
        data = db_manager.fetch_daily_data(stock_symbol, period=time_range)
        if data is None or data.empty:
            return go.Figure()

        return create_stock_graph(data, stock_symbol.upper(), sma_periods)

    except Exception as e:
        print(f"Error: {e}")
        return go.Figure()

def create_stock_graph(data, title, sma_periods):
    # Format the 'time' column to display only year, month, and day
    data['formatted_time'] = data['time'].dt.strftime('%Y-%m-%d')

    # Create a subplot with 2 rows and adjust the gap between the rows
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.15,
                        row_heights=[0.6, 0.3])

    # Add the candlestick trace
    candlestick = go.Candlestick(x=data['formatted_time'],
                                 open=data['open'],
                                 high=data['high'],
                                 low=data['low'],
                                 close=data['close'],
                                 name='Candlestick')

    fig.add_trace(candlestick, row=1, col=1)

    # Determine color for volume bars
    colors = ['green' if close >= open_ else 'red' for open_, close in zip(data['open'], data['close'])]

    # Add the volume trace
    volume = go.Bar(x=data['formatted_time'], y=data['volume'], marker_color=colors, name='Volume')

    fig.add_trace(volume, row=2, col=1)

    # Calculate the selected SMAs
    sma_data = pd.DataFrame()
    if 'sma_30' in sma_periods:
        sma_data['sma_30'] = data['close'].rolling(window=30).mean()
    if 'sma_50' in sma_periods:
        sma_data['sma_50'] = data['close'].rolling(window=50).mean()

    # Add the selected SMAs as lines on the candlestick graph
    for col in sma_data.columns:
        sma_line = go.Scatter(x=data['formatted_time'], y=sma_data[col], mode='lines', name=f'{col}', line=dict())
        fig.add_trace(sma_line, row=1, col=1)

    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        title_font_size=24,
        height=1000,
        xaxis2_rangeslider_visible=False,
        xaxis_type='category',
        xaxis2_type='category'
    )

    return fig

if __name__ == '__main__':
    # Define the local server URL
    local_url = "http://127.0.0.1:8050/"

    # Open a web browser and navigate to the local server URL
    webbrowser.open_new(local_url)

    # Run the Dash app server
    app.run_server(debug=True)
