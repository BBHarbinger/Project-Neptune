
from backend.data.fetch import fetch_stock_data
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Setting up the app layout
app.layout = html.Div([
    dcc.Input(id='stock-symbol', value='MSFT', type='text', debounce=True),
    dcc.Graph(id='stock-graph', style={"width": "100%", "height": "95vh"}),
    dcc.Interval(id='graph-update', interval=10 * 1000)  # 10 seconds (for dynamic updating, if needed)
], style={"width": "100%", "height": "100vh", "margin": "0"})


@app.callback(
    Output('stock-graph', 'figure'),
    [Input('stock-symbol', 'value'),
     Input('stock-graph', 'relayoutData')]
)

def interactive_candlestick(stock_symbol, relayoutData, time_series="daily", period="2y", ):
    df = fetch_stock_data(stock_symbol, time_series, period)

    if relayoutData and 'xaxis.range[0]' in relayoutData:
        x_start, x_end = relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']
        df = df[(df.index >= x_start) & (df.index <= x_end)]
        y_max = df['High'].max()
        y_min = df['Low'].min()
    else:
        y_max = df['High'].max()
        y_min = df['Low'].min()

    # Create a subplot with 2 rows and 1 column
    fig = make_subplots(rows=2, cols=1, row_heights=[0.67, 0.33], shared_xaxes=True, vertical_spacing=0.02)

    # Add candlestick trace
    fig.add_trace(go.Candlestick(x=df.index,
                                 open=df['Open'],
                                 high=df['High'],
                                 low=df['Low'],
                                 close=df['Close']),
                  row=1, col=1)

    # Determine the colors for the volume bars
    colors = ['green' if close >= open else 'red' for close, open in zip(df['Close'], df['Open'])]

    # Add volume bar trace
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors),
                  row=2, col=1)

    # Capitalize the first letter of time_series and update the title
    capitalized_time_series = time_series.capitalize()
    # Update the layout to style the plot
    fig.update_layout(
        autosize=True,
        title=f"{capitalized_time_series} chart for {stock_symbol}",
        title_x=0.5,  # this centers the title
        title_font=dict(size=24, family="Courier New, monospace", color="#7f7f7f"),
        xaxis_rangeslider_visible=False,  # hides the default range slider
        yaxis_title='Price',
    )

    if time_series == "monthly":
        options = list([
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=2, label="2y", step="year", stepmode="backward"),
            dict(step="all")
        ])
    elif time_series == "hourly" or time_series == "20min":
        options = list([
            dict(count=7, label="7d", step="day", stepmode="backward"),
            dict(count=14, label="14d", step="day", stepmode="backward"),
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(step="all")
        ])

    else:
        options = list([
            dict(count=7, label="7d", step="day", stepmode="backward"),
            dict(count=14, label="14d", step="day", stepmode="backward"),
            dict(count=1, label="1m", step="month", stepmode="backward"),
            dict(count=3, label="3m", step="month", stepmode="backward"),
            dict(count=6, label="6m", step="month", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=2, label="2y", step="year", stepmode="backward"),
            dict(step="all")
        ])

    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=options
        ),
        row=1, col=1  # Important! Apply the range slider only to the bottom subplot.
    )

    fig.update_yaxes(range=[y_min, y_max], row=1, col=1)

    return fig


