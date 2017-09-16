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

    def check_value(self):
        """The main loop"""
        try:
            usd_sell_ad = self.usd_best_ad('sell')
            cny_sell_ad = self.cny_best_ad('sell')
            cny_buy_ad = self.cny_best_ad( 'buy')
            print "@time:", datetime.datetime.utcnow()
            print "USD sell:", usd_sell_ad['temp_price'], "max value:", usd_sell_ad['max_amount_available'], "CNY sell:", cny_sell_ad['temp_price'], "max value:", cny_sell_ad['max_amount_available'], "CNY buy:", cny_buy_ad['temp_price'],"max value:", cny_buy_ad['max_amount_available']
            items = {'USD':
                     {'sell':
                      {'price':float(usd_sell_ad['temp_price']),'max_amount':int(usd_sell_ad['max_amount_available'])}},
                     'CNY':
                     {'sell':
                      {'price':float(cny_sell_ad['temp_price']),'max_amount':int(cny_sell_ad['max_amount_available'])},
                      'buy':
                      {'price':float(cny_buy_ad['temp_price']),'max_amount':int(cny_buy_ad['max_amount_available'])}}}
            with XlsxProcessor() as xlsm:
                xlsm.add_to_xlsx(items)

            if datetime.datetime.utcnow() >= self.report_time:
                mail = MailBuilder(type = MailType.REPORT)
                self.report_time = self.report_time + datetime.timedelta(days = 1)
                mail.build_body()
                mail.send()

        except NoDataException as e:
            print "Exception:", e.message
        finally:
            threading.Timer(20, self.check_value).start()
        

    def start(self):
        """Start the main loop"""
        self.check_value()

class NoDataException(Exception):
    """NoDataException raised if lbcapi returned an error data"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)