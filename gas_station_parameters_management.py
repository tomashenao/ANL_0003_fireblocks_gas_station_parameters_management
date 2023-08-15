import requests
import pandas as pd
from dateutil import tz
from pytz import timezone
from datetime import datetime, timedelta
import plotly.express as px
import numpy as np
import requests
import json
import fireblocks

def set_auto_fuel(vault_account_id: str, auto_fuel: bool) -> str:
    return fireblocks.set_auto_fuel(vault_account_id, auto_fuel)

auto_fuel_status = set_auto_fuel("0", True)

headers = {'Authorization': 'Bearer ' + '3G1so9dRH9LKYgx40m4Ygq7wImHbb4bU86gFA972'}

################ BTC ################
url = "https://api.cryptoquant.com/v1/btc/network-data/fees-transaction?window=day&limit=30"
data_list = requests.get(url, headers=headers).json()['result']['data']

# Create a pandas DataFrame
btc_daily_network_fees = pd.DataFrame(data_list).sort_values('date')

# Calculate the 7-day EMA of 'fees_transaction_mean'
btc_daily_network_fees['ema_7day'] = btc_daily_network_fees['fees_transaction_mean'].ewm(span=7, adjust=False).mean()
btc_daily_network_fees['wenia_withdrawal_fee'] = btc_daily_network_fees['ema_7day']*(1+0.5)
btc_daily_network_fees['date'] = pd.to_datetime(btc_daily_network_fees['date'])
btc_daily_network_fees = btc_daily_network_fees[btc_daily_network_fees['date'] < pd.to_datetime(datetime.now().date())]
btc_daily_network_fees = btc_daily_network_fees[['date', 'fees_transaction_mean', 'wenia_withdrawal_fee']]

# Print the resulting DataFrame
#print(btc_daily_network_fees)

url = "https://api.cryptoquant.com/v1/btc/network-data/fees-transaction?window=hour&limit=1"
data_list = requests.get(url, headers=headers).json()['result']['data']

# Create a pandas DataFrame
btc_hourly_network_fees = pd.DataFrame(data_list).sort_values('datetime')
btc_hourly_network_fees['datetime'] = pd.to_datetime(btc_hourly_network_fees['datetime'], utc=True)
btc_hourly_network_fees['datetime'] = btc_hourly_network_fees['datetime'].dt.tz_convert(timezone('America/Bogota'))
last_update = btc_hourly_network_fees['datetime']
btc_hourly_network_fees['date'] = btc_hourly_network_fees['datetime'].dt.strftime('%Y-%m-%d')
btc_hourly_network_fees['wenia_withdrawal_fee'] = btc_daily_network_fees.loc[btc_daily_network_fees['date'] == btc_daily_network_fees['date'].max(), 'wenia_withdrawal_fee'].values[0]
btc_hourly_network_fees = btc_hourly_network_fees[['date', 'fees_transaction_mean', 'wenia_withdrawal_fee']]
#print(btc_hourly_network_fees)

btc_daily_network_fees['wenia_withdrawal_fee'] = btc_daily_network_fees['wenia_withdrawal_fee'].shift(1)
btc_daily_network_fees = pd.concat([btc_daily_network_fees, btc_hourly_network_fees], axis=0).dropna()
btc_daily_network_fees['date'] = pd.to_datetime(btc_daily_network_fees['date'])
#print(btc_daily_network_fees)

btc_avg_deviation_from_wenia_fee = np.sqrt(sum((btc_daily_network_fees['wenia_withdrawal_fee']/btc_daily_network_fees['fees_transaction_mean']-1)**2)/len(btc_daily_network_fees))
btc_current_deviation_from_wenia_fee = btc_daily_network_fees.loc[btc_daily_network_fees['date'] == btc_daily_network_fees['date'].max(), 'wenia_withdrawal_fee'].values[0]/btc_daily_network_fees.loc[btc_daily_network_fees['date'] == btc_daily_network_fees['date'].max(), 'fees_transaction_mean'].values[0]-1
#print(btc_daily_network_fees)
#print(current_deviation_from_wenia_fee)

btcWithdrawalFees = px.line(data_frame=btc_daily_network_fees, x='date', y=['wenia_withdrawal_fee', 'fees_transaction_mean'], 
       labels={"date": 'Date',  "wenia_withdrawal_fee": "Wenia's Withdrawal Fee", 'fees_transaction_mean': 'Average Network Withdrawal Fee'})

################ ETH ################
url = "https://api.cryptoquant.com/v1/eth/network-data/fees-transaction?window=day&limit=30"
data_list = requests.get(url, headers=headers).json()['result']['data']

# Create a pandas DataFrame
eth_daily_network_fees = pd.DataFrame(data_list).sort_values('date')

# Calculate the 7-day EMA of 'fees_transaction_mean'
eth_daily_network_fees['ema_7day'] = eth_daily_network_fees['fees_transaction_mean'].ewm(span=7, adjust=False).mean()
eth_daily_network_fees['wenia_withdrawal_fee'] = eth_daily_network_fees['ema_7day']*(1+0.5)
eth_daily_network_fees['date'] = pd.to_datetime(eth_daily_network_fees['date'])
eth_daily_network_fees = eth_daily_network_fees[eth_daily_network_fees['date'] < pd.to_datetime(datetime.now().date())]
eth_daily_network_fees = eth_daily_network_fees[['date', 'fees_transaction_mean', 'wenia_withdrawal_fee']]

# Print the resulting DataFrame
#print(eth_daily_network_fees)

url = "https://api.cryptoquant.com/v1/eth/network-data/fees-transaction?window=hour&limit=1"
data_list = requests.get(url, headers=headers).json()['result']['data']

# Create a pandas DataFrame
eth_hourly_network_fees = pd.DataFrame(data_list).sort_values('datetime')
eth_hourly_network_fees['datetime'] = pd.to_datetime(eth_hourly_network_fees['datetime'], utc=True)
eth_hourly_network_fees['datetime'] = eth_hourly_network_fees['datetime'].dt.tz_convert(timezone('America/Bogota'))
last_update = eth_hourly_network_fees['datetime']
eth_hourly_network_fees['date'] = eth_hourly_network_fees['datetime'].dt.strftime('%Y-%m-%d')
eth_hourly_network_fees['wenia_withdrawal_fee'] = eth_daily_network_fees.loc[eth_daily_network_fees['date'] == eth_daily_network_fees['date'].max(), 'wenia_withdrawal_fee'].values[0]
eth_hourly_network_fees = eth_hourly_network_fees[['date', 'fees_transaction_mean', 'wenia_withdrawal_fee']]
#print(eth_hourly_network_fees)

eth_daily_network_fees['wenia_withdrawal_fee'] = eth_daily_network_fees['wenia_withdrawal_fee'].shift(1)
eth_daily_network_fees = pd.concat([eth_daily_network_fees, eth_hourly_network_fees], axis=0).dropna()
eth_daily_network_fees['date'] = pd.to_datetime(eth_daily_network_fees['date'])
#print(eth_daily_network_fees)

eth_avg_deviation_from_wenia_fee = np.sqrt(sum((eth_daily_network_fees['wenia_withdrawal_fee']/eth_daily_network_fees['fees_transaction_mean']-1)**2)/len(eth_daily_network_fees))
eth_current_deviation_from_wenia_fee = eth_daily_network_fees.loc[eth_daily_network_fees['date'] == eth_daily_network_fees['date'].max(), 'wenia_withdrawal_fee'].values[0]/eth_daily_network_fees.loc[eth_daily_network_fees['date'] == eth_daily_network_fees['date'].max(), 'fees_transaction_mean'].values[0]-1
#print(eth_daily_network_fees)
#print(current_deviation_from_wenia_fee)

ethWithdrawalFees = px.line(data_frame=eth_daily_network_fees, x='date', y=['wenia_withdrawal_fee', 'fees_transaction_mean'], 
       labels={"date": 'Date',  "wenia_withdrawal_fee": "Wenia's Withdrawal Fee", 'fees_transaction_mean': 'Average Network Withdrawal Fee'})


################ MATIC ################
#url = "https://api.cryptoquant.com/v1/erc20/network-data/fees-transaction?window=day&limit=30"
#data_list = pd.read_csv("Polygon_fees.csv")
#data_list = pd.DataFrame(data_list)
#data_list.columns = ['date', 'fees_transaction_mean']

# Create a pandas DataFrame
#matic_daily_network_fees = pd.DataFrame(data_list, columns=['date', 'fees_transaction_mean']).sort_values('date')

# Calculate the 7-day EMA of 'fees_transaction_mean'
#matic_daily_network_fees['ema_7day'] = matic_daily_network_fees['fees_transaction_mean'].ewm(span=7, adjust=False).mean()
#matic_daily_network_fees['wenia_withdrawal_fee'] = matic_daily_network_fees['ema_7day']*(1+0.75)
#matic_daily_network_fees['date'] = pd.to_datetime(matic_daily_network_fees['date']).dt.date
#matic_daily_network_fees = matic_daily_network_fees[matic_daily_network_fees['date'] > datetime.today().date()-timedelta(days=30)]
#matic_daily_network_fees = matic_daily_network_fees[['date', 'fees_transaction_mean', 'wenia_withdrawal_fee']]

# Print the resulting DataFrame
#print(matic_daily_network_fees)

#matic_daily_network_fees['wenia_withdrawal_fee'] = matic_daily_network_fees['wenia_withdrawal_fee'].shift(1)
#matic_daily_network_fees = matic_daily_network_fees.dropna()

#matic_avg_deviation_from_wenia_fee = np.sqrt(sum((matic_daily_network_fees['wenia_withdrawal_fee']/matic_daily_network_fees['fees_transaction_mean']-1)**2)/len(matic_daily_network_fees))
#matic_current_deviation_from_wenia_fee = matic_daily_network_fees.loc[matic_daily_network_fees['date'] == matic_daily_network_fees['date'].max(), 'wenia_withdrawal_fee'].values[0]/matic_daily_network_fees.loc[matic_daily_network_fees['date'] == matic_daily_network_fees['date'].max(), 'fees_transaction_mean'].values[0]-1
#print(eth_daily_network_fees)
#print(current_deviation_from_wenia_fee)

#maticWithdrawalFees = px.line(data_frame=matic_daily_network_fees, x='date', y=['wenia_withdrawal_fee', 'fees_transaction_mean'], 
       #labels={"date": 'Date',  "wenia_withdrawal_fee": "Wenia's Withdrawal Fee", 'fees_transaction_mean': 'Average Network Withdrawal Fee'})

url = "https://api.polygonscan.com/api"
params = {
    "module": "gastracker",
    "action": "gasoracle",
    "apikey": "VSEJDJABSPUWPTN3SQQWRQZGBI6MX8M35K"
}

response = requests.get(url, params=params)
data = response.json()
maticLastBlockFee = pd.DataFrame(data)

matic_current_deviation_from_wenia_fee = 1/(float(maticLastBlockFee.loc["suggestBaseFee", "result"])*0.03/70)-1

def send_slack_message(payload, webhook):
    """Send a Slack message to a channel via a webhook. 
    
    Args:
        payload (dict): Dictionary containing Slack message, i.e. {"text": "This is a test"}
        webhook (str): Full Slack webhook URL for your chosen channel. 
    
    Returns:
        HTTP response code, i.e. <Response [503]>
    """

    return requests.post(webhook, json.dumps(payload))

webhook = "https://hooks.slack.com/services/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"
payload = {"text": "Anomaly detected! Current Ethereum network fees are " + str(round(eth_current_deviation_from_wenia_fee, 2)*-100) + "% higher than Wenia's fees."}

if eth_current_deviation_from_wenia_fee*(-1) > (2)*eth_avg_deviation_from_wenia_fee:
    send_slack_message(payload, webhook)

payload = {"text": "Anomaly detected! Current Bitcoin network fees are " + str(round(btc_current_deviation_from_wenia_fee, 2)*-100) + "% higher than Wenia's fees."}

if btc_current_deviation_from_wenia_fee*(-1) > (2)*btc_avg_deviation_from_wenia_fee:
    send_slack_message(payload, webhook)

payload = {"text": "Anomaly detected! Current Polygon network fees are " + str(round(matic_current_deviation_from_wenia_fee, 2)*-100) + "% higher than Wenia's fees."}

if matic_current_deviation_from_wenia_fee < 0:
    send_slack_message(payload, webhook)
