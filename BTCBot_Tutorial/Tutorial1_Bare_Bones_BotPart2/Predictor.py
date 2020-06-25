class Predictor:
    def __init__(self, FeatureList, Model = None):
        #self.FiveMinMovAv = FiveMinMovingAverage.get_moving_av()
        self.features=FeatureList
        self.firstFiveeMinBlocker=0
        self.counterblocker=0
        if Model == None:
            self.model = [1]*len(FeatureList)
        else:
            self.model = Model


    def prediction(self):
            print("Average Change in price in 5 resamples(old)?", self.features[3].get_old_moving_av())
            moving_av=self.features[3].get_moving_av()
            if self.features[3].fiveMin[3:4]==[0,0]:
                return ("UnderThreeMin", 0, 0)
            elif moving_av < 0:
                return("sell" , 1 , self.features[0].get_value())
            elif moving_av > 1:
                if False == (self.features[3].zscore[0]>1.8 and self.features[3].fiveMin[0] >0):
                    if moving_av > 10 and moving_av<20:
                        return("buy", 0.25, self.features[1].get_value())
                    elif moving_av > 20:
                        return ("buy", 1, self.features[1].get_value())
                    else:
                        return("buy", .05, self.features[1].get_value())
                else:
                    return ("Do Nothing", 0, 0)
            else:
                return("Do Nothing", 0, 0)



    def hft_pred(self):
        if self.firstFiveeMinBlocker >20:###Make this a method
            if (self.features[3].new_entry_outlier_negative() and self.features[3].positive_momentum_n_time(True, 2)):  # HFT account
                print("Trying to track down -negative holding value line 41 in predicotr should not be negative", self.features[1].get_value())
                return ("buy", 1, self.features[1].get_value())
            else:
                return ("Do Nothing", 0, 0)
        else:
            self.firstFiveeMinBlocker+=1
            return ("Do Nothing", 0, 0)


    def two_hr_monetum(self):
        if self.features[3].two_hr_momentum() and not self.features[3].threeMinMomentum() :  # HFT account
            return ("buy", 0.5, self.features[1].get_value())
        elif(self.features[3].threeMinMomentum() ):
            return("sell", 1, self.features[0].get_value())
        else:
            return ("Do Nothing", 0, 0)


    def big_change_now(self):
        if self.features[3].postive_quick_change() and self.features[3].positive_momentum_n_time(False, 20):
            return ("buy", 0.5, self.features[1].get_value())
        elif not self.features[3].positive_momentum_n_time(False, 4):
            return("sell", 1, self.features[1].get_value())
        else:
            return ("Do Nothing", 0,0)



    def simple_8400_9700(self):
        if self.features[1].get_value() <8600 and self.features[1].get_value() >8400:
            return ("buy", 0.1, self.features[1].get_value())
        elif self.features[1].get_value() <8300 and self.features[1].get_value()>7900:
            return ("buy2", 1, self.features[1].get_value())
        elif self.features[1].get_value() >9700:
            return ("sell", 1, self.features[1].get_value())
        else:
            return ("Do Nothing", 0, 0)

    def hft2(self):
        if self.firstFiveeMinBlocker > 20:  ###Make this a method
            if (self.features[3].new_entry_outlier_negative() and self.features[3].fiveMin[1]<0) or (self.features[3].fiveMin[1] < -20 and self.features[3].fiveMin[0] < -20) :  # HFT account
                return ("buy", 1, self.features[1].get_value())
            else:
                return ("Do Nothing", 0, 0)
        else:
            self.firstFiveeMinBlocker += 1
            return ("Do Nothing", 0, 0)


    def hft2(self):
        if self.firstFiveeMinBlocker > 20:  ###Make this a method
            if (self.features[3].new_entry_outlier_negative() and self.features[3].fiveMin[1]<0) or (self.features[3].fiveMin[1] < -20 and self.features[3].fiveMin[0] < -20) :  # HFT account
                return ("buy", 1, self.features[1].get_value())
            else:
                return ("Do Nothing", 0, 0)
        else:
            self.firstFiveeMinBlocker += 1
            return ("Do Nothing", 0, 0)


    def hold_percent(self):
        if self.counterblocker>120:
            if (not self.features[3].positive_momentum_n_time(True, 3)) and (self.features[1].get_value() < 9300):#TODO this is hard coded which is complete crap
                currentBuyPrice = self.features[1].get_value()#TODO Either change the line above to daily low to daily low or make a GUI that can change that value during run time
                if currentBuyPrice != 0: #Sometimes there is a divide by zero error in the main func and I think It is coming from here.
                    return ("buy", 0.1, currentBuyPrice)#play around with amounts on this.... THis could be the new super money maker
                else:
                    ("Tried to divide by zero", 0 , 0)
            else:
                return ("Do Nothing", 0, 0)
        else:
            self.counterblocker+=1
            return ("Do Nothing", 0, 0)


#TODO This should be way improved. So That it buy after the it hits its bottom. In this case it can be buying while its going down then selling, then buying again. This could lead to substanial loss
    def todaysLow(self):
        if self.features[1].get_value() < ((self.features[4].get_past24hrLow()*0.001)+self.features[4].get_past24hrLow()):
            return ("buy", 0.1, self.features[1].get_value())
        elif self.features[1].get_value() < ((self.features[4].get_todaysLow()*0.001)+self.features[4].get_todaysLow()):
                return ("buy", 0.03, self.features[1].get_value())
        else:
            return ("Do Nothing", 0, 0)


    def todays_low_just_changed(self): #This should be way improved. #So That I buy after the it hits its bottom. In this case I can be buying while its going down then selling, then buying again. This could lead to substanial loss
        if self.features[4].did_last24hr_low_just_change():
            return ("buy", 0.1, self.features[1].get_value())
        elif self.features[4].did_todays_low_just_change():
                return ("buy", 0.03, self.features[1].get_value())
        else:
            return ("Do Nothing", 0, 0)