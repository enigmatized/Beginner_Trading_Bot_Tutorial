import inspect
import sys

import pandas

from DataSource import KrakenSource
from FeatureExtractor import *
from Predictor import Predictor
from datetime import datetime, timedelta
import time





class SimulateBot:
    def __init__(self):
        self.ks=KrakenSource()
        self.features=[]
        self.features.append(BidSellCurrentPrice(self.ks))
        self.BidSellCurrentValue=0
        self.sellPrice = 0
        self.features.append(AskBuyCurrentPrice(self.ks))
        self.buyPrice = 1
        self.features.append(PriceDelta(self.ks))
        self.features.append(FiveMinMovingAverage(self.ks))
        self.priceMomentumDirection = 3
        self.features.append(Low(self.ks))
        self.features.append(PriceVolume(self.ks))
        self.predictor = Predictor(self.features)
        self.boughtSold=[]

        #createFeatures put them in List
        #createPrediction using features
        #Set up Timer
        self.delay = 60  #In Seconds
        self.orderStatus = None
        self.KRAKENCOSTOFTRADE = 0.0022

        self.df = self.set_Up_Df() #sets up Data Frame

        #Associcated with 5min Moving Average###Very Bad Algo
        self.holding = 0#In BTC
        self.balance = 1000# In dollar
        self.totalBoughtCost=[]



        self.holdingTillGain=0
        self.balanceTillGain=1000
        self.ledgarOfHoldTillGain= []
        self.lastPurchaseTime=datetime.now() - timedelta(hours=24)###This needs to be improved.
        ##The time gap of purchasing is crap.
        self.nextTimeToPurchaseTillGain=0
        self.ledgar=[]#List of GenericDic

        self.genericDic = {"AmountBought": 0, "CostPreTax": 0, "CostPostTax": 0, "priceOfBTCAttime" :0  }




        self.holdingTillGainV2=0
        self.balanceTillGainV2=1000
        self.ledgarOfHoldTillGainV2= []
        self.lastPurchaseTimeV2=datetime.now() - timedelta(hours=24)###This needs to be improved.
        ##The time gap of purchasing is crap.
        self.nextTimeToPurchaseTillGainV2=0
        self.ledgarV2=[]#List of GenericDic

        self.genericDicV2 = {"AmountBought": 0, "CostPreTax": 0, "CostPostTax": 0, "priceOfBTCAttime" :0,  "HitTarget":False,"HighestPriceReached":0  }



    def dictionary_setter(self, dic, AmountBought, CostPreTax, CostPostTax,priceOfBTCAttime):
        dic["AmountBought"]=AmountBought
        dic["CostPreTax"] =CostPreTax
        dic["CostPostTax"] =CostPostTax
        dic["priceOfBTCAttime"] =priceOfBTCAttime
        return dic


    def dictionary_setterV2(self, dic, AmountBought, CostPreTax, CostPostTax,priceOfBTCAttime):#For the second version hold till trade adding in a form of trailing stop loss
        dic["AmountBought"]=AmountBought
        dic["CostPreTax"] =CostPreTax
        dic["CostPostTax"] =CostPostTax
        dic["priceOfBTCAttime"] =priceOfBTCAttime
        return dic



    def set_Up_Df(self):
        df = pandas.DataFrame(columns=["Time", "Type", "CurrentBuyPrice", "Buy/Sell",  "balance", "holding", "price_usd_PreKrakenTax", "price_usd_PostKrakenTax",  "Total_Profit"])
        return df

    def addToDF(self, types, buySell, balance, holding, preTax, postTax,  profit):
        self.df = self.df.append(
            {"Time": datetime.now(), "Type": types, "CurrentBuyPrice": self.features[1].get_value(),"Buy/Sell": buySell, "balance": balance , "holding":holding ,  "price_usd_PreKrakenTax": preTax, "price_usd_PostKrakenTax": postTax,  "Total_Profit": profit},
            ignore_index=True)


    def run(self):
        targetTime = datetime.now() + timedelta(hours=24)
        countCVSoutput=0# Counter for CSV output

        while True:
            #get prediction from predictor timed, take action based on prediction
            action, amount, btcPrice = self.predictor.prediction()
            if action == "buy" and self.balance>0:
                self.balance, self.holding, self.totalBoughtCost=self.buy("5min Average",
                                                                          self.balance*amount/btcPrice,
                                                                          self.balance, self.holding,
                                                                          self.totalBoughtCost)#name, amount, balance, holding, totalBoughtCost)
            elif action == "sell" and self.holding>0:
                self.balance, self.holding, self.totalBoughtCost=self.sell("5min Average",self.holding*amount, self.balance, self.holding, self.totalBoughtCost)
                self.totalBoughtCost=[]
            elif action == "Do Nothing":
                print("Prediction Method not Prepared to take action...Needs more data collecting time")
            else:
                self.raiseNotDefined()



            actionHoldTillGain, amount3, btc3 = self.predictor.hold_percent()##Update when to buy
            now = datetime.now()
            for holding in self.ledgarOfHoldTillGain:
                valueUSDofPastPurchaseInNowTerms = (self.features[self.sellPrice].get_value() * self.kraken_tranaction_cost_nonUSD(holding["AmountBought"]))
                percentageIwantToMake=0.005
                if holding["CostPreTax"]< (valueUSDofPastPurchaseInNowTerms - (valueUSDofPastPurchaseInNowTerms * percentageIwantToMake)):
                    self.balanceTillGain, self.holdingTillGain, ThrowAwayVariable = self.sell( #Throw away because no need to edit ledgar. Will be deleted below
                        "Hold Till a gain",
                        holding["AmountBought"],
                        self.balanceTillGain,
                        self.holdingTillGain,
                        holding, True)
                    self.ledgarOfHoldTillGain.remove(holding)
            if actionHoldTillGain == "buy" and self.balanceTillGain>300 and (len(self.ledgarOfHoldTillGain) <1 or((self.lastPurchaseTime + timedelta(hours=12)) < now)):
                self.lastPurchaseTime=now
                self.balanceTillGain, self.holdingTillGain, self.ledgarOfHoldTillGain = self.buy(
                    "Hold Till a gain",
                    (self.balanceTillGain * 0.3 / btc3),
                    self.balanceTillGain,
                    self.holdingTillGain,
                    self.ledgarOfHoldTillGain,
                    True)



            #actionHoldTillGain, amount3, btc3 = self.predictor.hold_percent()  ##Update when to buy
            #now = datetime.now()
            for holding in self.ledgarOfHoldTillGainV2:
                valueUSDofPastPurchaseInNowTerms = (
                            self.features[self.sellPrice].get_value() * self.kraken_tranaction_cost_nonUSD(
                        holding["AmountBought"]))
                percentageIwantToMake = 0.005
                if holding["CostPreTax"] < (
                        valueUSDofPastPurchaseInNowTerms - (valueUSDofPastPurchaseInNowTerms * percentageIwantToMake)):
                    if holding["HitTarget"]==True and (holding["HighestPriceReached"] >  self.features[self.sellPrice].get_value()*1.001):
                        self.balanceTillGainV2, self.holdingTillGainV2, ThrowAwayVariable = self.sell(
                            # Throw away because no need to edit ledgar. Will be deleted below
                            "Hold Till a gain",
                            holding["AmountBought"],
                            self.balanceTillGainV2,
                            self.holdingTillGainV2,
                            holding, True)
                        self.ledgarOfHoldTillGainV2.remove(holding)
                    elif holding["HitTarget"]==False:
                        holding["HitTarget"]=True
                        holding["HighestPriceReached"]=self.features[self.sellPrice].get_value()
                    elif (holding["HighestPriceReached"] <  self.features[self.sellPrice].get_value()):
                        holding["HighestPriceReached"]=self.features[self.sellPrice].get_value()
            if actionHoldTillGain == "buy" and self.balanceTillGainV2 > 300 and (
                    len(self.ledgarOfHoldTillGainV2) < 1 or ((self.lastPurchaseTimeV2 + timedelta(hours=12)) < now)):
                self.lastPurchaseTimeV2 = now
                self.balanceTillGainV2, self.holdingTillGainV2, self.ledgarOfHoldTillGainV2 = self.buy(
                    "Hold Till a gain",
                    (self.balanceTillGainV2 * 0.3 / btc3),
                    self.balanceTillGainV2,
                    self.holdingTillGainV2,
                    self.ledgarOfHoldTillGainV2,
                    True)



            print("Holding: ", self.holding,"Holding till Gain", self.holdingTillGain, "Holding till GainV2", self.holdingTillGainV2)
            print("Balance", self.balance,  "Balance till gain", self.balanceTillGain, "Balance till gainV2", self.balanceTillGainV2)


            time.sleep(self.delay)
            countCVSoutput+=1
            if countCVSoutput >10:
                countCVSoutput=0
                self.df.reset_index(drop=True, inplace=True)
                outfile = str(targetTime) + ".csv"
                outfile=outfile.replace(" ", "")
                outfile = outfile.replace(":", "_")
                outfile = outfile.replace(".", "_")
                outfile= outfile+ ".csv"
                self.df.to_csv('PositionsTraded/'+outfile)





    def buy(self, name, amount, balance, holding, ledgar, boughtCostTrueORFalse=False):
        print(name+ "Purchase Initiated")
        amountAfterKrakenTaxBTC = amount - amount * self.KRAKENCOSTOFTRADE
        dollarValuePreTax = self.features[1].get_value() * amount#make a check that the same self.features[1].get_value() is used for prediction as well
        afterKrakenTax = dollarValuePreTax - (dollarValuePreTax * self.KRAKENCOSTOFTRADE)
        holding+=amountAfterKrakenTaxBTC
        balance-=dollarValuePreTax
        totalBoughtCostAddition = []
        if boughtCostTrueORFalse:
            ledgar.append(self.dictionary_setter(self.genericDic, amountAfterKrakenTaxBTC, dollarValuePreTax, afterKrakenTax, self.features[self.buyPrice].get_value() ))
        else:
            ledgar.append(dollarValuePreTax)
        self.addToDF(name, "Buy",
                     balance, holding,
                     dollarValuePreTax, afterKrakenTax,
                     0)  #types, buySell, balance, holding, preTax, postTax,  profit)
        return  (balance, holding, ledgar)

        #self.balance, self.holding, self.totalBoughtCost= buy(amount, balance, holding, totalBoughtCost, "Low Strategy"))

    def sell(self, name, amountInBTC, balance, holding, ledgar, boughtCostTrueORFalse=False):
        print(name+ "Sell Initiated", "for a price of", self.features[self.sellPrice].get_value() )
        dollarValue = self.features[self.sellPrice].get_value() * amountInBTC
        afterKrakenTax = dollarValue - (dollarValue * self.KRAKENCOSTOFTRADE)
        holding-=amountInBTC
        balance+=afterKrakenTax
        if boughtCostTrueORFalse:
            self.addToDF(name, "Sell", balance, holding, dollarValue, afterKrakenTax, afterKrakenTax - ledgar["CostPreTax"])
        else:
            self.addToDF(name, "Sell", balance, holding, dollarValue, afterKrakenTax, afterKrakenTax - sum(ledgar))
            #totalBoughtCost=[]#This should be changed for sure. This eliminates thee to list, and I don't think I want to do that in everycase.
                    #There is cases where I wont sell the entire amount, only partial.
                    ##I think it work for this. #Will need to update
        return(balance, holding, ledgar)



    def update_highest_price_reached_in_lis(self, lis):
        highestValueAmountReachedInUSD = 4
        currentSellPrice = self.features[self.BidSellCurrentValue].get_value()
        for x in lis:
            if x[highestValueAmountReachedInUSD] < currentSellPrice:
                x[highestValueAmountReachedInUSD]=currentSellPrice
        return lis



    def raiseNotDefined(self):
        fileName = inspect.stack()[1][1]
        line = inspect.stack()[1][2]
        method = inspect.stack()[1][3]
        print("*** Something went wrong at: %s at line %s of %s" % (method, line, fileName))
        #sys.exit(1)

    def kraken_tranaction_cost_nonUSD(self, amount):
        return amount-(amount*self.KRAKENCOSTOFTRADE)


test =SimulateBot()
test.run()