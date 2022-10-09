import json
import os
import time

import schedule
from binance.um_futures import UMFutures

import sendMessage

proxies = {'https': 'http://127.0.0.1:7890'}


def calculate_ema(prices, days, smoothing=2):
    '''
    author = "techno_gssb"
    totally eqv. to talib.EMA
    '''
    ema = []
    for price in prices[1:days]:
        ema.append (float ("nan"))
    # ema = [sum(prices[:days]) / days]
    ema.append (sum (prices[:days]) / days)
    for price in prices[days:]:
        ema.append ((price * (smoothing / (1 + days))) + ema[-1] * (1 - (smoothing / (1 + days))))
    return ema


def job():
    with open ('./config.json', 'r') as fcc_file:
        fcc_data = json.load (fcc_file)
    um_futures_client = UMFutures (proxies=proxies)
    millis = int (round (time.time () * 1000))
    now = time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime (millis / 1000))
    now = time.mktime (time.strptime (now[0:-5] + "00:00", "%Y-%m-%d %H:%M:%S"))
    hour = int (now * 1000)
    timee = fcc_data['time']
    for sym in fcc_data['symbol']:
        symbol = sym
        try:
            status = fcc_data[sym]
        except:
            status = None
        data = um_futures_client.klines (symbol, timee)
        emarr144 = []
        for em in data:
            emarr144.append (float (em[4]))

        EMA21 = calculate_ema (emarr144, 21)[-1]
        EMA55 = calculate_ema (emarr144, 55)[-1]
        EMA144 = calculate_ema (emarr144, 144)[-1]
        print (EMA55, EMA144)
        if EMA144 > EMA55 > EMA21 and (status or status is None):
            fcc_data[sym] = False
            sendMessage.bark (symbol, "做空", fcc_data['barkUrl'], fcc_data['barkKey'])
        if EMA144 < EMA55 < EMA21 and ((not status) or status is None):
            fcc_data[sym] = True
            sendMessage.bark (symbol, "做多", fcc_data['barkUrl'], fcc_data['barkKey'])
        time.sleep (10)
    with open ("./config.json", "w") as f:
        json.dump (fcc_data, f)


if not os.path.exists ("./config.json"):
    print ("config文件不存在，请创建")
with open ('./config.json', 'r') as fcc_file:
    fcc_data = json.load (fcc_file)
sendMessage.bark ("开始运行", "test", fcc_data['barkUrl'], fcc_data['barkKey'])

schedule.every ().hour.do (job)
while True:
    schedule.run_pending ()
    time.sleep (1)
