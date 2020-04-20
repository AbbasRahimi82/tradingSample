import backtrader as bt
import backtrader.indicators as btind
import datetime as dt
import pandas as pd
import math
import datetime as dt
from datetime import datetime, timedelta
# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
    def notify_order(self,order):
        if order.status in [order.Submitted,order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED {}'.format(order.executed.price))
            elif order.issell():
                self.log('SELL EXECUTED {}'.format(order.executed.price))
            self.bar_executed= len(self)

        self.order = None


    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        if self.order: # we wont order if already out an order
            return
        if not self.position: # we buy if you are not in position

            if self.dataclose[0] < self.dataclose[-1]:
                # current close less than previous close

                if self.dataclose[-1] < self.dataclose[-2]:
                    # previous close less than the previous close

                    # BUY, BUY, BUY!!! (with all possible default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.buy()

        else :
            if len(self)>=(self.bar_executed+5): # check if 5 days passed by previous buy order
                self.log('SELL CREATED {}' .format(self.dataclose[0]) )
                self.order = self.sell()


class GoldenCross(bt.Strategy):
    params = (('fast',50),('slow',200),('order_percentage',0.95),('ticker','SPY'))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.fast_moving_average = bt.indicators.SMA(
            self.data.close,period=self.params.fast,plotname='{} day moving average'.format(self.params.fast)
        )
        self.slow_moving_average = bt.indicators.SMA(
            self.data.close,period=self.params.slow,plotname='{} day moving average'.format(self.params.slow)
        )
        self.crossover = bt.indicators.CrossOver(self.fast_moving_average,self.slow_moving_average)

    def next(self):
        if self.position.size == 0:
            if self.crossover > 0:
                amount_to_invest = (self.params.order_percentage * self.broker.cash)
                self.size = math.floor(amount_to_invest/self.data.close)
                print ("Buy {} shares of {} at {}".format(self.size,self.params.ticker,self.data.close[0]))
                self.buy(size=self.size)

        if self.position.size > 0:
            if self.crossover < 0 :
                print ("Sell {} shares of {} at {}".format(self.size, self.params.ticker, self.data.close[0]))
                self.close()


class BuyHold(bt.Strategy):
    def next(self):
        if self.position.size == 0:
            size = int(self.broker.getcash() / self.data)
            self.buy(size=size)


class VIXStrategy(bt.Strategy):

    def __init__(self):
        self.vix = self.datas[0].vixclose
        self.spyopen = self.datas[0].open
        self.spyclose = self.datas[0].close

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        if self.vix[0] > 35:
            self.log('Previous VIX, %.2f' % self.vix[0])
            self.log('SPY Open, %.2f' % self.spyopen[0])

            if not self.position or self.broker.getcash() > 5000:
                size = int(self.broker.getcash() / self.spyopen[0])
                print("Buying {} SPY at {}".format(size, self.spyopen[0]))
                self.buy(size=size)

        '''if len(self.spyopen) % 20 == 0:
            self.log("Adding 5000 in cash, never selling. I now have {} in cash on the sidelines".format(
                self.broker.getcash()))
            self.broker.add_cash(5000)'''
        if self.vix[0] < 15 and self.position:
            self.close()








