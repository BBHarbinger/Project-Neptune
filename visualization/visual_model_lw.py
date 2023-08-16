"""
File name: visual_model_lw.py
Description: This file is used to visualize the data using lightweight-charts
package (https://github.com/TechfaneTechnologies/pytvlwcharts.git)
[pip3 install -U git+https://github.com/TechfaneTechnologies/pytvlwcharts.git]
Author: Felix Yuzhou Sun
"""

pip3 install -U git+https://github.com/TechfaneTechnologies/pytvlwcharts.git
import pandas as pd
import requests
import numpy as np
from pytvlwcharts import Chart
import time
import asyncio
import nest_asyncio

nest_asyncio.apply()

