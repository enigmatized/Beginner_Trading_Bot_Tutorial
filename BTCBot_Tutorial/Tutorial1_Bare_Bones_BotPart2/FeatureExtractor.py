import collections
import time
from datetime import datetime
import pandas as pd
import DataSource
from scipy import stats
import numpy as np



class FiveMinMovingAverage:
    def __init__(self, datasource):
        self.TIMENEEDTOELSAPSEFORUPDATE = 60
        seconds = time.time()
        local_time = time.ctime(seconds)
        print("Seconds since epoch =", seconds)
        self.lastTimeUpdateInSeconds=seconds
        print("Local time:", local_time)
        self.lastTimeUpdate=local_time

        self.ds = datasource
        self.oldPrices=[]
        self.lastPrice = self.current_price()
        self.fiveMin=[0,0,0,0,0]
        self.zscore=[]
        self.x=self.get_moving_av()

        arr = []
        for i in range(2880):
            arr.append(0)
        self.twodayAverage = arr


    def current_price(self):
        data = self.ds.get_data()
        try: #NEED TO HANDLE THIS IN A MUCH BETTER WAY, THIS JUST DELAYS THE THREAD IF THERE IS AN ERROR, NOT SURE WHY I AM EVEN GETTING AN ERROR?
            return float(data['XXBTZUSD']['p'][0])#This throws an error at times. #Need to throw a try and catch block around this
        except:
            time.sleep(10)
            return float(data['XXBTZUSD']['p'][0])



    def get_value(self):
        current = self.current_price()
        print("Past PRice", self.lastPrice)
        print("Current PRice",self.current_price())
        delta = current - self.lastPrice
        print("Deltat#1",delta)
        #self.lastPrice = current
        return delta

    def update_5minaverage(self):
        if self.time_tracking():
            # print("Whqat is get_value()",tempNewVal)
            print("Whqat is lastPrice", self.lastPrice)
            print("What is self.currnet_price()", self.current_price())
            current = self.current_price()
            delta = current - self.lastPrice
            print("delta", delta)
            print( "fiveMin (old):", self.fiveMin)
            if delta != 0 and delta!=self.fiveMin[0]:
                self.lastPrice = current
                self.fiveMin=self.shift_insert_list(self.fiveMin)
                self.twodayAverage=self.shift_insert_list(self.twodayAverage)
                self.fiveMin[0]=delta
                self.twodayAverage[0]=delta
                print("fiveMin ( up):", self.fiveMin )
                self.outliers(self.fiveMin)
                print("21minute ", self.twodayAverage[0:20])
                self.print_out_avs()
                print("Update moving average!!!!!!!!!!!!!!!!!")
        else :
            print("Not Ready to update, Less than 60 Seconds have passed")
            print("")


    def shift_insert_list(self, listz):
        a_list = collections.deque(listz)
        a_list.rotate(1)
        return list(a_list)


    def get_delta_av_frame(self, min):
        minMinusZero=min-1
        return sum(self.twodayAverage[0:minMinusZero])/len(self.twodayAverage[0:minMinusZero])


    def giv_av(self, min):
        minMinusZero = min - 1
        zeroCheck = 0
        if zeroCheck in self.twodayAverage[0:minMinusZero]:
            return 0
        else:
            return self.get_delta_av_frame(min)




    def get_moving_av(self):
        self.update_5minaverage()
        return sum(self.fiveMin)/len(self.fiveMin)

    def get_old_moving_av(self):
        return sum(self.fiveMin)/len(self.fiveMin)

    def outliers(self, list):
        self.zscore = np.abs(stats.zscore(list))
        print("Z-score: ", self.zscore)

    def new_entry_outlier_negative(self):
        if self.fiveMin[0] < 0:
            z = np.abs(stats.zscore(self.fiveMin))
            if z[0] > 1.4 and not z[0] > 2.6:
                return True
            else:
                return False
        else:
            return False


    def moving_av_without_outlier(self):
        print()


    def time_tracking(self):
        tempTime=time.time()
        local_time = time.ctime(time.time())
        #print("NewTime Comparison ", tempTime)
        #print("Old Time ", self.lastTimeUpdateInSeconds)
        print("oldtime - temp time ", tempTime-self.lastTimeUpdateInSeconds," At Local time:", local_time)
        resultTime= tempTime-self.lastTimeUpdateInSeconds
        if resultTime > self.TIMENEEDTOELSAPSEFORUPDATE:
            self.lastTimeUpdateInSeconds=tempTime
            return True
        else:
            return False


    def print_out_avs(self):
        minarr=[10,20,30,45]
        for x in minarr:
            if self.giv_av(x) != 0:
                n=3*x/10
                print("Average Change in ", x, "min: ", self.giv_av(x),"  ",n, "LargestValues: ", self.nmaxelements(self.twodayAverage[0:x-1], int(n)))
        hrArr=[1,2,3,4,5,6,8,12,24]
        for x in hrArr:
            n=6
            if self.giv_av(x*60) != 0:
                print("Average Change in ", x, "hr: ", self.giv_av(x*60),"  ",n, "LargestValues: ", self.nmaxelements(self.twodayAverage[0:(x*60)-1], int(n)))

    def nmaxelements(self, list1, N):
        final_list = []
        tempJ=[]
        for i in range(0, N):
            max1 = 0
            for j in range(len(list1)):
                if j not in tempJ:
                    if abs(list1[j]) > abs(max1):
                        max1 = list1[j]
                        tempJ.append(j)
            final_list.append(max1)
        return final_list

    def two_hr_momentum(self):
        minute_momnetumer=[5, 10, 20, 30, 40, 60, 90, 120]
        if self.twodayAverage[90] == 0:
            print("Not 90min past")
            if self.twodayAverage[91] == 0:
                return False
        scoreTrack=0
        for time in minute_momnetumer:
            if self.giv_av(time) > 0:
                scoreTrack=scoreTrack+1
        if scoreTrack >= 7:
            print("90min Past")
            return True
        else:
            return False

    def threeMinMomentum(self):
        if self.giv_av(3) > 0:
            return True
        else:
            return False



    def postive_quick_change(self):
        postivecount=0
        negativecount = 0
        for x in self.twodayAverage[0:6]:
            if x>20:
                postivecount+=1
            if x<-20:
                negativecount+=1
        if postivecount>negativecount:
            return True
        else:
            return False

    def positive_momentum_n_time(self, hrs=True,times=3 ):#same implementation as 2hr, need to change to make a custom time
        minute_momnetumer=[]
        if hrs:
            minutes=times*60
            for i in range(int(minutes)):
                if i in [10, 20, 30, 40, 60, 90, 120, 150, 180, 240,300,360]:
                    minute_momnetumer.append(i)
        elif hrs == False :
            m = []
            for i in range(times):
                minute_momnetumer.append(i)
        if self.twodayAverage[-1] == 0:
            if self.twodayAverage[-2] == 0:
                print("Not 90min past")
                return False
        scoreTrack=0
        for time in minute_momnetumer:
            if self.giv_av(time) > 0:
                scoreTrack=scoreTrack+1
        if scoreTrack >= int(0.8*len(minute_momnetumer)):
            return True
        else:
            return False







class PriceVolume:
    def __init__(self, dataSource):
        self.dataSource=dataSource
        self.pricedf=None
        self.volume= None

        #self.df = pandas.DataFrame(columns=["Type", "Price", "time"])

    def get_price(self):
        prricedf=None#obviously this needs to be changed, just trying to eliminate error-age
        return prricedf



    def get_value(self):
        self.data=self.dataSource.get_data()
        #utilizew data to come up with a value
        #return value
        return 0

    #def get_data




class AskBuyCurrentPrice:
    def __init__(self, datasource):
        self.ds = datasource

    def get_value(self):
        data = self.ds.get_data()
        amount= float(data['XXBTZUSD']['a'][0])
        if amount<200:
            print("Major Error")
            return 9999999  # ErrorCode
        elif amount != 0:
            return amount
        else:
            print("Major Error")
            return 9999999 # ErrorCode


class BidSellCurrentPrice:
    def __init__(self, datasource):
        self.ds = datasource


    def get_value(self):
        data = self.ds.get_data()
        amount= float(data['XXBTZUSD']['b'][0])
        if amount != 0:
            return amount
        else:
            print("Major Error")
            return 9999999 # ErrorCode



class PriceCurrent:
    def __init__(self, datasource):
        self.ds = datasource


    def get_value(self):
        data = self.ds.get_data()
        amount= float(data['XXBTZUSD']['p'][0])
        if amount != 0:
            return amount
        else:
            print("Error")
            return 9999999 # ErrorCode



class PriceDelta:
    def __init__(self, datasource):
        self.ds = datasource
        self.lastPrice = self.current_price()


    def current_price(self):
        data = self.ds.get_data()
        return float(data['XXBTZUSD']['p'][0])

    def get_value(self):
        current = self.current_price()
        delta = current - self.lastPrice
        self.lastPrice = current
        return delta

class Low:#TODO Note today's Low is constantly chaning on Kraken...Meaning it gives different information everymin, but that information is usally the same different lows.
    def __init__(self, datasource):
        self.ds = datasource
        now = datetime.now().time()
        self.past24hrLow =self.get_past24hrLow()
        self.todaysLow=self.get_todaysLow()
        self.past24hrLowList = [[self.get_past24hrLow(), now]]
        self.todaysLowList = [[self.get_todaysLow(), now]]
        self.todaysLowListJustPrice=[]
        self.count=0


    def get_past24hrLow(self):
        data = self.ds.get_data()
        return float(data['XXBTZUSD']['l'][1])

    def get_todaysLow(self):
        data = self.ds.get_data()
        return float(data['XXBTZUSD']['l'][0])


    def did_todays_low_just_change(self): #Note this method is only really effective at buying at lows after the first 12hrs of a day
        now = datetime.now().time()#Also Time Zone could lead to issues here?
        if now.hour <2:
            print("Under The 1hr Mark")
            self.todaysLowListJustPrice=[]
            return False
        elif now.hour < 10:#Changed to 10hrs
            print("Under The 10hr Mark")
            if self.get_todaysLow() not in self.todaysLowListJustPrice:
                self.todaysLowListJustPrice.append(self.get_todaysLow())
            return False
        elif self.count<20: #This is in case of starting after 10am
            self.count+=1
            if self.get_todaysLow() not in self.todaysLowListJustPrice:
                print("adding self.get_todaysLow() to list")
                self.todaysLowListJustPrice.append(self.get_todaysLow())
                print(self.todaysLowListJustPrice)
        elif self.get_todaysLow() in self.todaysLowListJustPrice:
                print("self.todaysLow in self.todaysLowListJustPrice", self.get_todaysLow(), self.todaysLowListJustPrice)
        else:
            print("self.todaysLow NOT in self.todaysLowListJustPrice", self.get_todaysLow(), self.todaysLowListJustPrice)
            self.todaysLowListJustPrice.append(self.get_todaysLow())
            self.todaysLow = self.get_todaysLow() #TODO Why is this not updating or chaning?
            print("did self.todaysLow change", self.todaysLow)
            return True

    def did_last24hr_low_just_change(self):#This might be terrible logic
        if self.past24hrLow == self.get_past24hrLow():
            return False
        elif self.past24hrLow > self.get_past24hrLow():
            self.past24hrLow = self.get_past24hrLow()#I should create a set up, where if it goes below a 24 low, it can buy there, but pauses its buy are does a trailing stop lowss for a purchase
            return True
        else:
            print("Not equal to 24hr low, but not lower than past 24hr low.")
            print("Need to write an algo or come up with a strategy to deal with all these situations")
            return False





class High:
    def __init__(self, datasource):
        self.ds = datasource
        self.past24hrHi = self.get_past24hrHi()
        self.todaysHi = self.get_todaysHi()

    def get_past24hrHi(self):
        data = self.ds.get_data()
        return float(data['XXBTZUSD']['h'][1])

    def get_todaysHi(self):
        data = self.ds.get_data()
        return float(data['XXBTZUSD']['l'][0])



