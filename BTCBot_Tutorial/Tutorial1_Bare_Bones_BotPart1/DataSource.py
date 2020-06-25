import json
import datetime

import requests
import pandas as pd
import time

KRAKEN_SERVER_TIME = 'https://api.kraken.com/0/public/Time'
PUBLIC_TICKER_API_URL_BTC = 'https://api.kraken.com/0/public/Ticker?pair='
Bitcoin = 'xbtusd'




def get_time():
    response=requests.get(KRAKEN_SERVER_TIME)
    response_json = response.json()
    return response_json['result']

def get_recent_data(crypto):
    response = requests.get(PUBLIC_TICKER_API_URL_BTC + crypto)
    try:
        response_json = response.json()
        return response_json['result']
    except:
        print("Error In Get Recent Data: ", response)
        return {}


def main():
    responseTest = get_recent_data(Bitcoin)
    print('Main function inside Data Source Ran Successfully')
    print(responseTest)
    practice = KrakenSource()
    print(type(responseTest['XXBTZUSD']['p'][0]))


class DataSource:
    def __init__(self, KrakenSource):
        self.krakenDF = KrakenSource
        #self.data=
        self.data = KrakenSource

    def get_data(self):
        return self.get_data()





class KrakenSource():
    def __init__(self):
        self.data = self.get_recent_data(Bitcoin)
        #print(self.data)
        self.updateDelay = datetime.timedelta(seconds=58)####time of request
        self.lastUpdate = datetime.datetime.now() - self.updateDelay

    def get_recent_data(self, crypto):
        response = requests.get(PUBLIC_TICKER_API_URL_BTC + crypto)
        response_json = response.json()
        return response_json['result']

    def get_data(self):
        self.update()
        return self.data

    def update(self):
        if datetime.datetime.now() > self.lastUpdate + self.updateDelay:
            self.lastUpdate = datetime.datetime.now()
            self.data = get_recent_data(Bitcoin)


main()


#
# <pair_name> = pair name
#     a = ask array(<price>, <whole lot volume>, <lot volume>),
#     b = bid array(<price>, <whole lot volume>, <lot volume>),
#     c = last trade closed array(<price>, <lot volume>),
#     v = volume array(<today>, <last 24 hours>),
#     p = volume weighted average price array(<today>, <last 24 hours>),
#     t = number of trades array(<today>, <last 24 hours>),
#     l = low array(<today>, <last 24 hours>),
#     h = high array(<today>, <last 24 hours>),
#     o = today's opening price