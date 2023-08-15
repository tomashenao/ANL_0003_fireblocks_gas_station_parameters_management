import requests
import pandas as pd
from dateutil import tz
from pytz import timezone
from datetime import datetime, timedelta
import plotly.express as px
import numpy as np
import requests
import json
from fireblocks_sdk import FireblocksSDK
import math

# Import last 30 days of Ethereum gas fees from CryptoQuant API
headers = {'Authorization': 'Bearer ' + '3G1so9dRH9LKYgx40m4Ygq7wImHbb4bU86gFA972'}
url = "https://api.cryptoquant.com/v1/eth/network-data/gas?window=day&limit=30"
data_list = requests.get(url, headers=headers).json()['result']['data']

# Create a pandas DataFrame
ethereum_daily_avg_gas_prices = pd.DataFrame(data_list).sort_values('date')[['date', 'gas_price_mean']]

# Calculate the IQR (Interquartile Range)
q1 = ethereum_daily_avg_gas_prices['gas_price_mean'].quantile(0.25)
q3 = ethereum_daily_avg_gas_prices['gas_price_mean'].quantile(0.75)
iqr = q3 - q1

# Calculate the upper outlier threshold
upper_threshold = str(math.ceil(q3 + 1.5 * iqr))

print(upper_threshold)

api_secret = open('/Users/tomhenra/Documents/Wenia/Risk Management/Gas Station Management/ANL_0003_fireblocks_gas_station_parameters_management/sweeping_fireblocks.key', 'r').read()
api_key = '567af12e-48cb-d54e-e4c0-27c7c5ba671d'
#api_url = 'https://sandbox-api.fireblocks.io' 
fireblocks = FireblocksSDK(api_secret, api_key)

def set_auto_fuel(vault_account_id: str, auto_fuel: bool) -> str:
    return fireblocks.set_auto_fuel(vault_account_id, auto_fuel)

auto_fuel_status = set_auto_fuel("0", True)

def configure_gas_station(gas_threshold: str, gas_cap: str, max_gas_price: str):
    fireblocks.set_gas_station_configuration(gas_threshold=gas_threshold, gas_cap=gas_cap, max_gas_price=max_gas_price)
    
gas_station_conf = configure_gas_station("0.005", "0.01", "20")

