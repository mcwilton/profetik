from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime
import datetime
import math
# import emoji
import time
import re
import ccxt
import requests
import cryptocompare
from forex_python.bitcoin import BtcConverter
from forex_python.converter import CurrencyRates
from forex_python.converter import CurrencyCodes
from blockcypher import get_address_overview


bitmex = ccxt.bitmex()
bittrex = ccxt.bittrex()
kraken = ccxt.kraken()


bitmex_price = f"Bitmex for $ {bitmex.fetch_ticker('BTC/USD')['close']}"
bittrex_price = f"Bittrex for $ {bittrex.fetch_ticker('BTC/USD')['close']}"
kraken_price = f"Kraken for $ {kraken.fetch_ticker('BTC/USD')['close']}"

all_prices_loop = [bitmex_price, bittrex_price, kraken_price]


def hilow():
    highest_price = max(all_prices_loop)
    lowest_price = min(all_prices_loop)
    arbitrage_high = highest_price.split()[3]
    arbitrage_low = lowest_price.split()[3]
    arbitrage = float(arbitrage_high) - float(arbitrage_low)
    return f"Buy on {lowest_price} and sell on {highest_price}. Your arbitrage gain is ${round(arbitrage, 2)}"


def rates():
    current_price = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    json_data = current_price.json()
    return f"USD{str(json_data['bpi']['USD']['rate_float'])}"


def check_usd_bitcoin_value(amount):
    validate = requests.get(f"https://blockchain.info/tobtc?currency=USD&value={amount}")
    data = validate.json()
    return data


def qrcode(request, incoming_msg):
    bit_address = incoming_msg.split()[1]
    qr_code_url = f'https://www.bitcoinqrcodemaker.com/api/?style=bitcoin&address={bit_address}'
    return qr_code_url


def check_date(request, date):
    match_date = re.search(r'\d{2}.\d{2}.\d{4}', date)
    date = datetime.strptime(match_date.group(), '%d.%m.%Y').date()
    currency = date.split()[0].upper()
    symbols = CurrencyCodes()
    bit_amount = float(re.search(r'\d+', date).group(0))
    past_date = BtcConverter()
    reply = past_date.convert_btc_to_cur_on(bit_amount, currency, date)
    message = f"{bit_amount} Bitcoins were worth {symbols.get_symbol(currency)}{round(reply, 2)}"


def get_address(request, address):
    address_request = requests.post('https://api.blockcypher.com/v1/btc/test3/addrs')
    address = address_request.json()
    return f"Bitcoin address: {str(address['address'])}, Private key: {str(address['private'])}, {str(address['public'])}, {str(address['wif'])}"


def latest(request, latest_msg):
    currency = latest_msg.split()[4].upper()
    amount = float(re.search(r'\d+', latest_msg).group(0))
    symbols = CurrencyCodes()
    latest_price = BtcConverter()
    reply = latest_price.convert_btc_to_cur(amount, currency)
    return f"The latest price of B{amount} to {currency} is {symbols.get_symbol(currency)}{round(reply, 2)}"


def index(request):
    high_low = hilow()
    rate = rates()
    cryptoco = cryptocompare.get_price(['BTC'], ['ZAR', 'NGN', 'KES', 'GHC', 'TZS'])
    cryptoco_za = cryptoco['BTC']['ZAR']
    context = {
        "high_low" : high_low,
        "cryptoco_za" : cryptoco_za,
        "rate" : rate,
    }
    return render (request, "index.html", context)