from lbcapi import api
from xlsxproc import XlsxProcessor
from mailntf import MailBuilder, MailType
import json, threading, time, os, datetime, pytz

class Monitor:
    """Monitor deal with connection and loop"""
    def __init__(self):
        """Establish connection using keys.json file"""
        with open('./keys.json') as f:
            keys = json.load(f)
        self.__hmac_key = keys["READ"]["key"]
        self.__hmac_secret = keys["READ"]["secret"]
        self.__conn = api.hmac(self.__hmac_key, self.__hmac_secret)
        # Set email notification time
        self.set_reporttime()
        # Set optimal rate status
        self.__optrate = {'rate':6.3, 'time':datetime.datetime.utcnow()-datetime.timedelta(hours=1)}

    def set_reporttime(self, hour = 22, minute = 0, tmz = 'Asia/Shanghai'):
        dt_bj = datetime.datetime(2017, 1, 1, hour, minute, tzinfo = pytz.timezone(tmz))
        dt_now = datetime.datetime.utcnow()
        dt_utc = datetime.datetime.combine(dt_now.date(), dt_bj.astimezone(pytz.utc).time())
        if dt_now >= dt_utc:
            self.report_time = dt_utc + datetime.timedelta(days = 1)
        else:
            self.report_time = dt_utc

    def get_public_ads(self, sellorbuy, currency, method):
        """Get public ads by connection

        Args:
            conn: Connection returned by api.hmac
            sellorbuy: string 'sell' or 'buy'
            currency: string of currency, example: 'CNY', 'USD'
            method: string of payment method, example: 'paypal', 'alipay'

        Returns:
            A dictionary responsed by server
        """
        json_response = self.__conn.call('GET', '/' + sellorbuy + '-bitcoins-online/' + currency + '/' + method + '/.json').json()
        try:
            return json_response['data']['ad_list']
        except:
            raise NoDataException(json_response['error']['message'])

    @staticmethod
    def get_first_ad(ads):
        """Get the first ad

        Args: 
            ads: Ads dictionary server returned

        Returns: 
            The first ad, always the best
        """
        return ads[1]['data']

    @staticmethod
    def get_max_value(ad1, ad2):
        """Get the ad with max price"""
        if float(ad1['temp_price']) > float(ad2['temp_price']):
            return ad1
        else:
            return ad2

    @staticmethod
    def get_min_value(ad1, ad2):
        """Get the ad with min price"""
        if float(ad1['temp_price']) < float(ad2['temp_price']):
            return ad1
        else:
            return ad2

    def usd_best_ad(self, sellorbuy):
        """Return best ad in USD"""
        return self.get_first_ad(self.get_public_ads(sellorbuy, 'USD', 'paypal'))

    def cny_best_ad(self, sellorbuy):
        """Return best ad in CNY"""
        cny_sell_ad_wechat = self.get_first_ad(self.get_public_ads(sellorbuy, 'CNY', 'wechat'))
        cny_sell_ad_alipay = self.get_first_ad(self.get_public_ads(sellorbuy, 'CNY', 'alipay'))
        if sellorbuy == 'sell':
            return self.get_max_value(cny_sell_ad_wechat, cny_sell_ad_alipay)
        else:
            return self.get_min_value(cny_sell_ad_wechat, cny_sell_ad_alipay)

    def refine_output(self, cny_buy_ad, cny_sell_ad, usd_sell_ad):
        c2u = self.get_rate(float(cny_buy_ad['temp_price']), float(usd_sell_ad['temp_price']))
        c2u_net = self.get_netrate(float(cny_buy_ad['temp_price']), float(usd_sell_ad['temp_price']))
        items = {'USD':
                 {'sell':
                  {'price':float(usd_sell_ad['temp_price']),
                   'min_amount':int(usd_sell_ad['min_amount']),
                   'max_amount':int(usd_sell_ad['max_amount_available'])}},
                 'CNY':
                 {'sell':
                  {'price':float(cny_sell_ad['temp_price']),
                   'min_amount':int(cny_sell_ad['min_amount']),
                   'max_amount':int(cny_sell_ad['max_amount_available'])},
                  'buy':
                  {'price':float(cny_buy_ad['temp_price']),
                   'min_amount':int(cny_buy_ad['min_amount']),
                   'max_amount':int(cny_buy_ad['max_amount_available'])}},
                 'rate':
                 {'C2U':c2u},
                 'net_rate':
                 {'C2U':c2u_net},
                 }
        c2u_avl = self.get_avl_amount(items['CNY']['buy']['min_amount'], items['CNY']['buy']['max_amount'], 
                                      items['USD']['sell']['min_amount'], items['USD']['sell']['max_amount'],
                                      items['CNY']['buy']['price'], items['USD']['sell']['price'])
        items['available'] = {'C2U': c2u_avl}
        return items

    def check_value(self):
        """The main loop"""
        try:
            usd_sell_ad = self.usd_best_ad('sell')
            cny_sell_ad = self.cny_best_ad('sell')
            cny_buy_ad = self.cny_best_ad( 'buy')
            items = self.refine_output(cny_buy_ad, cny_sell_ad, usd_sell_ad)
            print "@time:", datetime.datetime.utcnow()
            print "USD sell:", usd_sell_ad['temp_price'], "max value:", usd_sell_ad['max_amount_available'], "CNY sell:", cny_sell_ad['temp_price'], "max value:", cny_sell_ad['max_amount_available'], "CNY buy:", cny_buy_ad['temp_price'],"max value:", cny_buy_ad['max_amount_available'], "C2U rate:", items['rate']['C2U'], "C2U netrate:", items['net_rate']['C2U'], "Available in CNY", items['available']['C2U']['inAd1']
            
            # Log to xlsx
            with XlsxProcessor() as xlsm:
                xlsm.add_to_xlsx(items)

            # Send notification
            rate = items['net_rate']['C2U']
            amount = items['available']['C2U']['inAd1'][1]
            if rate < self.__optrate['rate'] and amount > 500:
                mail = MailBuilder(type = MailType.NOTIFY)
                mail.build_body("Current transter rate of CNY->USD: " + str(rate) + " with maximun amount: " + str(amount))
                mail.send()
                self.__optrate['rate'] = rate
                self.__optrate['time'] = datetime.datetime.utcnow()
            elif datetime.datetime.utcnow() > self.__optrate['time'] + datetime.timedelta(hours = 1):
                self.__optrate['rate'] = 6.3

            # Send report
            if datetime.datetime.utcnow() >= self.report_time:
                self.report_time = self.report_time + datetime.timedelta(days = 1)
                mail = MailBuilder(type = MailType.REPORT)
                mail.build_body()
                mail.send()

        except NoDataException as e:
            print "Exception:", e.message
        finally:
            threading.Timer(600, self.check_value).start()
    
    @staticmethod
    def get_rate(price1, price2):
        """Using direct quotation"""
        return price1 / price2

    @staticmethod
    def get_netrate(price1, price2, amount = 0.01):
        """Using direct quotation"""
        pr2_fee_perc = 0.044
        pr2_fee_cons = 0.3
        return (price1 * amount) / (price2 * amount * (1 - pr2_fee_perc) - pr2_fee_cons)

    @staticmethod
    def get_avl_amount(ad1min, ad1max, ad2min, ad2max, ad1rate, ad2rate):
        min1 = ad1min / ad1rate
        min2 = ad2min / ad2rate
        max1 = ad1max / ad1rate
        max2 = ad2max / ad2rate
        if min1 <= max2 and max1 >= min2:
            minamount = max(min1, min2)
            maxamount = min(max1, max2)
            return {'inBTC': [minamount,maxamount], 
                    'inAd1': [minamount* ad1rate,maxamount* ad1rate] , 
                    'inAd2': [minamount* ad2rate,maxamount* ad2rate]}
        else:
            return {'inBTC': [0,0], 
                    'inAd1': [0,0] , 
                    'inAd2': [0,0]}

    def start(self):
        """Start the main loop"""
        self.check_value()

class NoDataException(Exception):
    """NoDataException raised if lbcapi returned an error data"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)