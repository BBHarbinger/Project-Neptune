from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool
from data.fetch import StockDatabaseManager
import pandas as pd

# Initialize the database manager and fetch data
db_manager = StockDatabaseManager()
db_manager.initialize_db()
data = db_manager.fetch_daily_data(stock_symbol="TSLA", period="5y")  # Corrected symbol

# Check if data is fetched successfully
if data is None:
    raise ValueError("Failed to fetch data.")

# Convert the datetime format from pandas (if necessary)
data['time'] = pd.to_datetime(data['time'])

# Output to static HTML file
output_file("stock_data.html")

# Create a new plot with a datetime axis type
p = figure(title="TSLA stock prices", x_axis_type="datetime", plot_width=800, plot_height=400)

# Add a line renderer with legend for closing prices
p.line(data['time'], data['close'], legend_label="Close Price", line_width=2)

# Add tools
hover = HoverTool(
    tooltips=[
        ("Date", "@time{%F}"),
        ("Close", "@close"),
    ],
    formatters={
        '@time': 'datetime',  # use 'datetime' formatter for '@time' field
    },
    mode='vline'
)

p.add_tools(hover)

# Show the results
show(p)
