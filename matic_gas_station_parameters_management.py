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
import os

# Import last 30 days of Ethereum gas fees from CryptoQuant API
#headers = {'Authorization': 'Bearer ' + '3G1so9dRH9LKYgx40m4Ygq7wImHbb4bU86gFA972'}
#url = "https://api.cryptoquant.com/v1/eth/network-data/gas?window=day&limit=30"
#data_list = requests.get(url, headers=headers).json()['result']['data']

print(os.path.exists("/Users/tomhenra/Documents/Wenia/Risk Management/Gas Station Management/ANL_0003_fireblocks_gas_station_parameters_management/polygon_daily_avg_gas_price.csv"))

# Import csv with Polygon network fee data
polygon_daily_avg_gas_prices = pd.DataFrame(pd.read_csv("/Users/tomhenra/Documents/Wenia/Risk Management/Gas Station Management/ANL_0003_fireblocks_gas_station_parameters_management/polygon_daily_avg_gas_price.csv"))

# Calculate the IQR (Interquartile Range)
q1 = polygon_daily_avg_gas_prices['gas_price_in_gwei'].quantile(0.25)
q3 = polygon_daily_avg_gas_prices['gas_price_in_gwei'].quantile(0.75)
iqr = q3 - q1

# Calculate the upper outlier threshold
upper_threshold = str(math.ceil(q3 + 1.5 * iqr))

# Calculate the fueling amount
expected_crypto_deposits_2023 = 83000
share_of_crypto_deposits_on_polygon_network = 0.8
share_of_clients_without_matic = 0.8
fueling_amount = (expected_crypto_deposits_2023*share_of_crypto_deposits_on_polygon_network*share_of_clients_without_matic/(3*30))*polygon_daily_avg_gas_prices['avg_transaction_fee_amount'].mean()
fueling_threshold = fueling_amount/3

fueling_amount = str(round(fueling_amount, 6))
fueling_threshold = str(round(fueling_threshold, 6))

print(upper_threshold)
print(fueling_amount)
print(fueling_threshold)

api_secret = open('/Users/tomhenra/Documents/Wenia/Risk Management/Gas Station Management/ANL_0003_fireblocks_gas_station_parameters_management/sweeping_fireblocks.key', 'r').read()
api_key = '567af12e-48cb-d54e-e4c0-27c7c5ba671d'
#api_url = 'https://sandbox-api.fireblocks.io' 
fireblocks = FireblocksSDK(api_secret, api_key)

#def set_auto_fuel(vault_account_id: str, auto_fuel: bool) -> str:
    #return fireblocks.set_auto_fuel(vault_account_id, auto_fuel)

#auto_fuel_status = set_auto_fuel("0", True)

def configure_gas_station(gas_threshold: str, gas_cap: str, max_gas_price: str):
    fireblocks.set_gas_station_configuration(gas_threshold=gas_threshold, gas_cap=gas_cap, max_gas_price=max_gas_price)
    
gas_station_conf = configure_gas_station(fueling_threshold, fueling_amount, upper_threshold)

