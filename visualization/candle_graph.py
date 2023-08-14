import plotly.graph_objects as go

from data.fetch import fetch_stock_data


def interactive_candlestick(stock_symbol, time_series="daily", period="max"):
    df = fetch_stock_data(stock_symbol, time_series, period)

    fig = go.Figure(data=[go.Candlestick(x=df.index,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])

    # Capitalize the first letter of time_series and update the title
    capitalized_time_series = time_series.capitalize()

    # Set the title and center it
    fig.update_layout(
        title=f"<b> {capitalized_time_series} chart for {stock_symbol}<b>",
        title_x=0.5,  #centers the title
        title_font=dict(size=24, family="Courier New, monospace", color="#7f7f7f")
    )

    fig.show()
