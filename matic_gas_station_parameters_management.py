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

# CryptoQuant API access
headers = {'Authorization': 'Bearer ' + '3G1so9dRH9LKYgx40m4Ygq7wImHbb4bU86gFA972'}

# Define token names and URLs
token_data = {
    'btc': {
        'inflow_url': "https://api.cryptoquant.com/v1/btc/exchange-flows/inflow?exchange=all_exchange&window=day&from=20230101&limit=230",
        'price_url': "https://api.cryptoquant.com/v1/btc/market-data/price-ohlcv?window=day&from=20230101&limit=230"
    },
    'eth': {
        'inflow_url': "https://api.cryptoquant.com/v1/eth/exchange-flows/inflow?exchange=all_exchange&window=day&from=20230101&limit=230",
        'price_url': "https://api.cryptoquant.com/v1/eth/market-data/price-ohlcv?window=day&from=20230101&limit=230"
    },
    'matic': {
        'inflow_url': "https://api.cryptoquant.com/v1/erc20/exchange-flows/inflow?token=matic&exchange=all_exchange&window=day&from=20230101&limit=230",
        'price_url': "https://api.cryptoquant.com/v1/erc20/market-data/price-ohlcv?token=matic&window=day&from=20230101&limit=230"
    },
    'usdc': {
        'inflow_url': "https://api.cryptoquant.com/v1/stablecoin/exchange-flows/inflow?token=usdc&exchange=all_exchange&window=day&from=20230101&limit=230",
        'price_url': "https://api.cryptoquant.com/v1/stablecoin/market-data/price-ohlcv?token=usdc&window=day&from=20230101&limit=230"
    }
}

merged_dfs = []

for token, urls in token_data.items():
    # Fetch inflow data
    inflow_data_list = requests.get(urls['inflow_url'], headers=headers).json()['result']['data']
    inflow_df = pd.DataFrame(inflow_data_list).sort_values('date')[['date', 'inflow_total']]
    
    # Fetch price data
    price_data_list = requests.get(urls['price_url'], headers=headers).json()['result']['data']
    price_df = pd.DataFrame(price_data_list).sort_values('date')[['date', 'close']]
    
    # Merge data frames
    merged_df = pd.merge(inflow_df, price_df, on='date', how='inner')
    merged_df[f'{token}_inflow_total_usd'] = merged_df['inflow_total'] * merged_df['close']
    merged_df = merged_df[['date', f'{token}_inflow_total_usd']]
    
    merged_dfs.append(merged_df)

# Merge all token data frames
merged_df = merged_dfs[0]
for df in merged_dfs[1:]:
    merged_df = pd.merge(merged_df, df, on='date', how='inner')

# Set 'date' column as the index
merged_df.set_index('date', inplace=True)

# Calculate the daily share of inflows via the MATIC network and USDC v MATIC
merged_df['matic_inflow_share'] = merged_df['matic_inflow_total_usd'] / merged_df.sum(axis=1)
merged_df['matic_inflow_share_using_usdc'] = merged_df['usdc_inflow_total_usd'] / (merged_df['usdc_inflow_total_usd']+merged_df['matic_inflow_total_usd'])

# We import the data from CryptoQuant's Query
queryid = '64dcdcb6cff19e0c797e4b85' #input query id 

url = "https://open-api.cryptoquant.com/open/v1/analytics/{}".format(queryid)
data = (requests.get(url, headers=headers).json())

#Defining Column Names for Dataframe
column_data = data['result']['columns']
column_labels = []
for column_name in column_data:
    column_labels.append(column_name['name'])
    
#creating Dataframe   
results = data['result']['results']
polygon_daily_avg_gas_prices = pd.DataFrame([results][0])
polygon_daily_avg_gas_prices.columns = column_labels
polygon_daily_avg_gas_prices = polygon_daily_avg_gas_prices.sort_values('day',ascending=True)

print(polygon_daily_avg_gas_prices)

# Calculate the IQR (Interquartile Range) of gas price in gwei
q1 = polygon_daily_avg_gas_prices['gas_price_in_gwei'].quantile(0.25)
q3 = polygon_daily_avg_gas_prices['gas_price_in_gwei'].quantile(0.75)
iqr_gwei = q3 - q1

upper_threshold = q3 + 1.5*iqr_gwei
upper_threshold = str(round(upper_threshold, 6))

# Calculate the IQR (Interquartile Range) of average transaction fee amount
q1 = polygon_daily_avg_gas_prices['avg_transaction_fee_amount'].quantile(0.25)
q3 = polygon_daily_avg_gas_prices['avg_transaction_fee_amount'].quantile(0.75)
iqr_avg_trx = q3 - q1

avg_trx_fee_outlier = q3 + 1.5*iqr_avg_trx

# Import MATIC OHLCV prices from all exchanges from CryptoQuant API
url = "https://api.cryptoquant.com/v1/erc20/market-data/price-ohlcv?token=matic&window=hour&limit=1"
data_list = requests.get(url, headers=headers).json()['result']['data']

# Calculate MATIC last hour close price
matic_latest_close_price = float(pd.DataFrame(data_list).at[0, 'close'])
# Calculate the upper outlier threshold (15USD / MATIC price). In this case we use 15USD which is consider the 
# price of the labor hour of an operations worker and we turn this to MATIC Gwei.
#upper_threshold = str(math.ceil((15/matic_latest_close_price) * 1000000000))

# Calculate the fueling amount
expected_monthly_crypto_deposits_2023 = 17000
expected_monthly_wenia_users = 14000
expected_monthly_deposits_by_user = expected_monthly_crypto_deposits_2023/expected_monthly_wenia_users
#share_of_crypto_deposits_on_polygon_network = merged_df['matic_inflow_share'].mean()
#share_of_clients_without_matic = merged_df['matic_inflow_share_using_usdc'].mean()
#fueling_amount = (expected_monthly_crypto_deposits_2023*share_of_crypto_deposits_on_polygon_network*share_of_clients_without_matic/(3*30))*polygon_daily_avg_gas_prices['avg_transaction_fee_amount'].mean()*7
fueling_amount = avg_trx_fee_outlier
fueling_threshold = polygon_daily_avg_gas_prices['avg_transaction_fee_amount'].mean()*1.5

print(fueling_amount/(polygon_daily_avg_gas_prices['avg_transaction_fee_amount'].mean()*expected_monthly_deposits_by_user))

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