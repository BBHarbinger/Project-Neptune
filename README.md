# Project-Neptune
A system that analyze the market data.
Gonna use Dash structure.

File structure:

/Project-Nepture
|-- /assets  # help make the app visually appealing
|   |-- styles.css
|
|-- /callbacks  # Define how the chart updates based on user input, like changing the time frame, zooming, or panning.
|   |-- chart_callbacks.py
|   |-- analysis_callbacks.py
|   |-- ...
|
|-- /components
|   |-- model
|   |-- news_feed
|   |-- visulization    # primary 
|   |-- screener_tools
|
|-- /data
|   |-- fetch_data.py
|
|-- /layouts    # define the overall layout, including the trading chart, a sidebar for selecting indicators, and a bottom panel for volume or other analysis.
|   |-- main_layout.py
|   |-- analysis_layout.py
|   |-- ...
|
|-- main.py / app.py
|-- index.py
|-- README
