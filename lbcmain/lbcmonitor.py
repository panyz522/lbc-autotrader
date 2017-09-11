from lbcapi import api
from openpyxl import Workbook
from openpyxl import load_workbook
import os.path
import urlparse, json, sched, threading, time, pip, os

path = os.getcwd()
with open('./keys.json') as f:
    keys = json.load(f)
hmac_key = keys["READ"]["key"]
hmac_secret = keys["READ"]["secret"]
conn = api.hmac(hmac_key, hmac_secret)

def get_public_ads(conn, sellorbuy, currency, method):
    """Get public ads by connection

    Args:
        conn: Connection returned by api.hmac
        sellorbuy: string 'sell' or 'buy'
        currency: string of currency, example: 'CNY', 'USD'
        method: string of payment method, example: 'paypal', 'alipay'

    Returns:
        A dictionary responsed by server
    """
    json_response = conn.call('GET', '/' + sellorbuy + '-bitcoins-online/' + currency + '/' + method + '/.json').json()
    return json_response['data']['ad_list']

def get_first_ad(ads):
    """Get the first ad

    Args: 
        ads: Ads dictionary server returned

    Returns: 
        The first ad, always the best
    """
    return ads[1]['data']

def get_max_value(ad1, ad2):
    """Get the ad with max price"""
    if float(ad1['temp_price']) > float(ad2['temp_price']):
        return ad1
    else:
        return ad2

def get_min_value(ad1, ad2):
    """Get the ad with min price"""
    if float(ad1['temp_price']) < float(ad2['temp_price']):
        return ad1
    else:
        return ad2

def usd_best_ad(conn, sellorbuy):
    """Return best ad in USD"""
    return get_first_ad(get_public_ads(conn, sellorbuy, 'USD', 'paypal'))

def cny_best_ad(conn, sellorbuy):
    """Return best ad in CNY"""
    cny_sell_ad_wechat = get_first_ad(get_public_ads(conn, sellorbuy, 'CNY', 'wechat'))
    cny_sell_ad_alipay = get_first_ad(get_public_ads(conn, sellorbuy, 'CNY', 'alipay'))
    if sellorbuy == 'sell':
        return get_max_value(cny_sell_ad_wechat, cny_sell_ad_alipay)
    else:
        return get_min_value(cny_sell_ad_wechat, cny_sell_ad_alipay)

def add_to_xlsx(file_name, items):
    """Add a dictionary to the last row in xlsm

    Args:
        file_name: The file name to be created
        items: Include info of every columns
    """
    file_path = './' + file_name
    if os.path.isfile(file_path):
        wb = load_workbook(file_path)
    else:
        wb = Workbook()
        ws = wb.active
        ws['a1'] = 'Time'
        ws['b1'] = 'USD-sell price'
        ws['c1'] = ws['e1'] = ws['g1'] = 'amount'
        ws['d1'] = 'CNY-sell price'
        ws['f1'] = 'CNY-buy price'
    ws = wb.active
    row = ws.max_row + 1
    ws['a'+ str(row)] = time.ctime()
    ws['b'+ str(row)] = items['USD']['sell']['price']
    ws['c'+ str(row)] = items['USD']['sell']['max_amount']
    ws['d'+ str(row)] = items['CNY']['sell']['price']
    ws['e'+ str(row)] = items['CNY']['sell']['max_amount']
    ws['f'+ str(row)] = items['CNY']['buy']['price']
    ws['g'+ str(row)] = items['CNY']['buy']['max_amount']
    wb.save(file_path)
    wb.close()

def check_value():
    """The main loop"""
    usd_sell_ad = usd_best_ad(conn, 'sell')
    cny_sell_ad = cny_best_ad(conn, 'sell')
    cny_buy_ad = cny_best_ad(conn, 'buy')
    print "@time:", time.ctime()
    print "USD sell:", usd_sell_ad['temp_price'], "max value:", usd_sell_ad['max_amount_available']
    print "CNY sell:", cny_sell_ad['temp_price'], "max value:", cny_sell_ad['max_amount_available']
    print "CNY buy:", cny_buy_ad['temp_price'], "max value:", cny_buy_ad['max_amount_available']
    items = {'USD':
             {'sell':
              {'price':float(usd_sell_ad['temp_price']),'max_amount':int(usd_sell_ad['max_amount_available'])}},
             'CNY':
             {'sell':
              {'price':float(cny_sell_ad['temp_price']),'max_amount':int(cny_sell_ad['max_amount_available'])},
              'buy':
              {'price':float(cny_buy_ad['temp_price']),'max_amount':int(cny_buy_ad['max_amount_available'])}}}
    add_to_xlsx("output.xlsx",items)
    threading.Timer(60.0, check_value).start()

check_value()


