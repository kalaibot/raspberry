#!/usr/bin/env python

import requests
from datetime import datetime
from slack import WebClient
import time
import os

api_token = os.environ['FINNHUB_API_TOKEN']
slack_api_token = os.environ['SLACK_API_TOKEN']
#cryptos_symbols = ['BINANCE:HBARBUSD', 'BINANCE:MANABUSD', 'BINANCE:ONEBUSD', 'BINANCE:ADABUSD', 'BINANCE:VETBUSD', 'BINANCE:ENJBUSD', 'BINANCE:KNCBUSD', 'BINANCE:BATBUSD']
cryptos_symbols = ['BINANCE:ADABUSD', 'BINANCE:VETBUSD']
# cryptos_symbols = os.environ['SYMBOLS']
# cryptos_bought = os.environ['CRYPTOS_BOUGHT']
cryptos_bought = {
    'ADABUSD': {'low': '1.10', 'mod': '1.20', 'high': '2.00'},
    'VETBUSD': {'low': '0.06', 'mod': '0.07', 'high': '0.100'}
}

def alert_high(crypto_name):

    if crypto_name in cryptos_bought:
        val = cryptos_bought.get(crypto_name)
        return float(val.get('high'))

def alert_low(crypto_name):

    if crypto_name in cryptos_bought:
        val = cryptos_bought.get(crypto_name)
        return float(val.get('low'))

def alert_mod(crypto_name):

    if crypto_name in cryptos_bought:
        val = cryptos_bought.get(crypto_name)
        return float(val.get('mod'))


datetime_object = str(datetime.now())
current = datetime_object.split(' ')
current_year = int(current[0].split('-')[0])
current_month = int(current[0].split('-')[1])
current_date = int(current[0].split('-')[2])
current_hour = int(current[1].split(':')[0])
current_minute = int(current[1].split(':')[1])

to_unix_timestamp = int(datetime(current_year, current_month, current_date, current_hour, current_minute).timestamp())
from_unix_timestamp = to_unix_timestamp - 60

# Finnhub api endpoint
crypto_price_url = "https://finnhub.io/api/v1/crypto/candle"
client = WebClient(token=slack_api_token)

for cryptos in cryptos_symbols:
    crypto_params = {"symbol": cryptos, "token": api_token, "resolution": "1", "from": from_unix_timestamp, "to": to_unix_timestamp}
    response = requests.get(crypto_price_url, crypto_params)
    time.sleep(2)
    if response.status_code == 429:
        client.chat_postMessage(channel='#crypto_alerts',
                                text=f" Around {datetime_object} -> API Limits exceeded for Finnhub api in {crypto_params['symbol']} alert")
    else:
        try:
            json_data = response.json()
            response.raise_for_status()
            closing_price_json = json_data['c']
            closing_price = closing_price_json[0]
            price_data = round(closing_price, 3)
            crypto = cryptos.split(':')[1]
            if price_data >= alert_high(crypto) or alert_low(crypto) <= price_data <= alert_mod(crypto):
                client.chat_postMessage(channel='#crypto_alerts',
                                        text=f" {datetime_object} -> {crypto_params['symbol']} price: {price_data}")

        except KeyError as err:
            client.chat_postMessage(channel='#crypto_alerts',
                                    text=f" Around {datetime_object} -> check the crypto_params-{err} in {crypto_params['symbol']} alert")