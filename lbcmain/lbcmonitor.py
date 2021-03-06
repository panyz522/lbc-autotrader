from lbcapi import api
from xlsxproc import XlsxProcessor
from dataexplorer import DataExplorer
from mailntf import MailBuilder, MailType
from config import Config
import json, threading, time, os, datetime, pytz

class Monitor:
    """Monitor deal with connection and loop"""
    def __init__(self):
        """Establish connection using keys.json file"""
        self.config = Config.get_monitorconfig()
        # Get keys and establish connection
        with open('./keys.json') as f:
            keys = json.load(f)
        self.__hmac_key = keys["READ"]["key"]
        self.__hmac_secret = keys["READ"]["secret"]
        self.__conn = api.hmac(self.__hmac_key, self.__hmac_secret)
        # Set email notification time
        self.set_reporttime(self.config["report_hours"], self.config["report_minutes"], self.config["report_tz"])
        # Set optimal rate status
        self.__optrate = {'rate':self.config["trans_threshold"], 'time':datetime.datetime.utcnow()-datetime.timedelta(hours=1)}

    def set_reporttime(self, hour = 22, minute = 0, tmz = 'Asia/Shanghai'):
        """Set daily report sending schedule according to hour:minite in speicific time zone
        
        You can get the list of timezone from pytz.all_timezones 
        """
        # Convert local target time to UTC time, get UTC current datetime, and combine UTC target time with UTC current date
        dt_bj = datetime.datetime(2017, 1, 1, hour, minute, tzinfo = pytz.timezone(tmz))
        dt_now = datetime.datetime.utcnow()
        dt_utc = datetime.datetime.combine(dt_now.date(), dt_bj.astimezone(pytz.utc).time())

        # Check if current time is later than target time, if so add one more day
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
        """Get the first ad's data"""
        try:
            return ads[0]['data']
        except IndexError as e:
            return None;

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
        if cny_sell_ad_wechat is None:
            return cny_sell_ad_alipay
        if cny_sell_ad_alipay is None:
            return cny_sell_ad_wechat
        if sellorbuy == 'sell':
            return self.get_max_value(cny_sell_ad_wechat, cny_sell_ad_alipay)
        else:
            return self.get_min_value(cny_sell_ad_wechat, cny_sell_ad_alipay)

    def refine_output(self, cny_buy_ad, cny_sell_ad, usd_sell_ad):
        """Convert ads to data dictionary
        
        Put useful information in each ad into a dictionary 
        then calculate and add additional information to the dictionary
        """
        c2u = self.get_rate(float(cny_buy_ad['temp_price']), float(usd_sell_ad['temp_price']))
        items = {'USD':
                 {'sell':
                  {'price':float(usd_sell_ad['temp_price']),
                   'min_amount':self.get_minint(usd_sell_ad['min_amount']),
                   'max_amount':self.get_maxint(usd_sell_ad['max_amount_available'])}},
                 'CNY':
                 {'sell':
                  {'price':float(cny_sell_ad['temp_price']),
                   'min_amount':self.get_minint(cny_sell_ad['min_amount']),
                   'max_amount':self.get_maxint(cny_sell_ad['max_amount_available'])},
                  'buy':
                  {'price':float(cny_buy_ad['temp_price']),
                   'min_amount':self.get_minint(cny_buy_ad['min_amount']),
                   'max_amount':self.get_maxint(cny_buy_ad['max_amount_available'])}},
                 'rate':
                 {'C2U':c2u},
                 }
        c2u_avl = self.get_avl_amount(items['CNY']['buy']['min_amount'], items['CNY']['buy']['max_amount'], 
                                      items['USD']['sell']['min_amount'], items['USD']['sell']['max_amount'],
                                      items['CNY']['buy']['price'], items['USD']['sell']['price'])
        c2u_net = self.get_netrate(float(cny_buy_ad['temp_price']), float(usd_sell_ad['temp_price']), c2u_avl['inBTC'][0])
        items['available'] = {'C2U': c2u_avl}
        items['net_rate'] = {'C2U':c2u_net}
        return items

    def get_maxint(self, str):
        """for max_amount"""
        if str is None:
            return 10000000
        else:
            return int(str)

    def get_minint(self, str):
        """for min_amount"""
        if str is None:
            return 0
        else:
            return int(str)

    def check_value(self):
        """The main loop"""
        try:
            usd_sell_ad = self.usd_best_ad('sell')
            cny_sell_ad = self.cny_best_ad('sell')
            cny_buy_ad = self.cny_best_ad( 'buy')
            items = self.refine_output(cny_buy_ad, cny_sell_ad, usd_sell_ad)
            itemtime = datetime.datetime.utcnow()
            print "[", itemtime, "]",
            print "USD sell:", usd_sell_ad['temp_price'], "max value:", usd_sell_ad['max_amount_available'], "CNY sell:", cny_sell_ad['temp_price'], "max value:", cny_sell_ad['max_amount_available'], "CNY buy:", cny_buy_ad['temp_price'],"max value:", cny_buy_ad['max_amount_available'], "C2U rate:", items['rate']['C2U'], "C2U netrate:", items['net_rate']['C2U'], "Available in CNY", items['available']['C2U']['inAd1']
            
            # Log to xlsx
            with XlsxProcessor() as xlsm:
                xlsm.add_to_xlsx(items)

            # Log to json
            with DataExplorer(index = 'testindex') as exp:
                exp.add_item(itemtime, items)

            # Send notification
            rate = items['net_rate']['C2U']
            amount = items['available']['C2U']['inAd1'][1]
            if rate < self.__optrate['rate'] and amount > self.config["min_amount"]:
                mail = MailBuilder(type = MailType.NOTIFY)
                mail.build_body("Current transter rate of CNY->USD: " + str(rate) + " with maximun amount: " + str(amount))
                mail.send()
                self.__optrate['rate'] = rate
                self.__optrate['time'] = datetime.datetime.utcnow()
            elif datetime.datetime.utcnow() > self.__optrate['time'] + datetime.timedelta(hours = 1):
                self.__optrate['rate'] = self.config["trans_threshold"];

            # Send report
            if datetime.datetime.utcnow() >= self.report_time:
                self.report_time = self.report_time + datetime.timedelta(days = 1)
                mail = MailBuilder(type = MailType.REPORT)
                mail.build_body()
                mail.send()

        except NoDataException as e:
            # Only deal with NoDataException here
            print "Exception:", e.message
        finally:
            pass
    
    @staticmethod
    def get_rate(price1, price2):
        """Using direct quotation"""
        return price1 / price2

    def get_netrate(self, price1, price2, amount = 0.01):
        """Using direct quotation"""
        pr2_fee_perc = self.config["fee_percent"]
        pr2_fee_cons = self.config["fee_constant"]
        return (price1 * amount) / (price2 * amount * (1 - pr2_fee_perc) - pr2_fee_cons)

    @staticmethod
    def get_avl_amount(ad1min, ad1max, ad2min, ad2max, ad1rate, ad2rate):
        """Get available simultaneous transaction amount"""
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
        self.stop()
        self.timer = MonitorTimer(self.check_value, self.config['interval'])
        self.timer.start()

    def stop(self):
        """Stop the main loop"""
        try:
            if self.timer.is_alive():
                self.timer.stop()
        except AttributeError:
            pass

class NoDataException(Exception):
    """NoDataException raised if lbcapi returned an error data"""
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

class MonitorTimer(threading.Thread):
    def __init__(self, loopmethod, waitingtime):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.loopmethod = loopmethod
        self.wait = waitingtime

    def run(self):
        while not self.event.is_set():
            self.loopmethod()
            self.event.wait(self.wait)

    def stop(self):
        self.event.set()