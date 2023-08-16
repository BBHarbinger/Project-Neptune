# File name: main.py
# Description: Main script to run the application
# Author: Felix Yuzhou Sun
# Verson 0.0.1

# 1.Dash version

from components.visualization.visual_model_plotly import app
import webbrowser
import threading

# Function to open the web page
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# Delayed browser opening
threading.Timer(1, open_browser).start()

if __name__ == '__main__':
    app.run_server(debug=True)



#2. lightweight_charts version

