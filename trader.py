from datetime import datetime

import backtrader as bt
import os
import pandas_datareader.data as data
import wget

from strategies import VIXStrategy
import pandas as pd

cerebro = bt.Cerebro()
cerebro.broker.setcash(100000)


def read_vix(ticker):
    url = "http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vixcurrent.csv"
    wget.download(url, 'vixcurrent.csv')
    df_vix = pd.read_csv('vixcurrent.csv', header=1)
    os.remove('vixcurrent.csv')
    df_vix['Date'] = pd.to_datetime(df_vix['Date'].astype('Datetime64'))
    df_vix['Date'] = df_vix['Date'].dt.strftime('%Y-%m-%d')
    df_vix = df_vix[df_vix['Date'] >= '2015-01-01']
    df_vix.to_csv('vix.csv',index=False)

    start = datetime(2015, 1, 1)
    end = datetime.now()
    ticker_data = data.DataReader(ticker, 'yahoo', start, end).reset_index()
    ticker_data['Date'] = pd.to_datetime(ticker_data['Date'].astype('Datetime64'))
    ticker_data['Date'] = ticker_data['Date'].dt.strftime('%Y-%m-%d')
    pd.merge(left=ticker_data, right=df_vix, on='Date').to_csv('spy_vix.csv',index=False)

    return df_vix


class SPYVIXData(bt.feeds.GenericCSVData):
    lines = ('vixopen', 'vixhigh', 'vixlow', 'vixclose',)

    params = (
        ('dtformat', '%Y-%m-%d'),
        ('date', 0),
        ('spyhigh', 1),
        ('spylow', 2),
        ('spyopen', 3),
        ('spyclose', 4),
        ('spyvolume', 5),
        ('spyadjclose', 6),
        ('vixopen', 7),
        ('vixhigh', 8),
        ('vixlow', 9),
        ('vixclose', 10)
    )


class VIXData(bt.feeds.GenericCSVData):
    params = (
        ('dtformat', '%Y-%m-%d'),
        ('date', 0),
        ('vixopen', 1),
        ('vixhigh', 2),
        ('vixlow', 3),
        ('vixclose', 4),
        ('volume', -1),
        ('openinterest', -1)
    )


ticker = 'AAPL'
read_vix(ticker)
csv_file = "spy_vix.csv"
vix_csv_file = "vix.csv"

spyVixDataFeed = SPYVIXData(dataname=csv_file)
vixDataFeed = VIXData(dataname=vix_csv_file)
cerebro.adddata(spyVixDataFeed)
cerebro.adddata(vixDataFeed)

cerebro.addstrategy(VIXStrategy)

cerebro.run()
cerebro.plot(volume=False)
