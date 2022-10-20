import json
import os
import time

import schedule
from binance.um_futures import UMFutures
from colorama import init

from util import getTime, loadConfig
from indicators import calculate_ema, normalizeMacd, RSI, SMA

init (autoreset=True)
import sendMessage


def vegas(closeData, configData, status, symbolKey):
    VegasRate = configData['VegasRate']
    EMA21 = calculate_ema (closeData, 21)[-1]
    EMA55 = calculate_ema (closeData, 55)[-1]
    EMA144 = calculate_ema (closeData, 144)[-1]
    nowTime = getTime ()
    print (nowTime, symbolKey, "\033[1;34m EMA144:\033[0m", EMA144, "\033[1;33m EMA55:\033[0m", EMA55,
           "\033[1;31m EMA21:\033[0m", EMA21)
    if abs (closeData[-1] - EMA144) / EMA144 <= float (VegasRate) and status is None:
        signal = "vegas开单"
        configData[symbolKey] = True
        return signal
    else:
        try:
            configData.pop (symbolKey)
        except Exception as e:
            print ("\033[1;31m " + repr (e) + "\033[0m")
        return None


def EMA2155144(closeData, configData, status, symbolKey):
    EMA21 = calculate_ema (closeData, 21)[-1]
    EMA55 = calculate_ema (closeData, 55)[-1]
    EMA144 = calculate_ema (closeData, 144)[-1]
    nowTime = getTime ()
    print (nowTime, symbolKey, "\033[1;34m EMA144:\033[0m", EMA144, "\033[1;33m EMA55:\033[0m", EMA55,
           "\033[1;31m EMA21:\033[0m", EMA21)
    signal = None
    if not ((EMA144 > EMA55 > EMA21) or (EMA144 < EMA55 < EMA21)):
        try:
            configData.pop (symbolKey)
        except Exception as e:
            print ("\033[1;31m " + repr (e) + "\033[0m")
    elif EMA144 > EMA55 > EMA21 and (status is None):
        configData[symbolKey] = False
        signal = "做空"
    elif EMA144 < EMA55 < EMA21 and (status is None):
        configData[symbolKey] = True
        signal = "做多"
    return signal


def NmacdeRsi(closeData, configData, status, symbolKey):
    NmacdRsiRate = configData['NmacdRsiRate']
    nowTime = getTime ()
    signal = None
    macNorm, trigger = normalizeMacd (closeData)
    rsi, rsiSma = RSI (closeData)
    SMA13 = SMA (closeData, 13)[-1]
    print (nowTime, symbolKey,
           "\033[1;34m macNorm:\033[0m", macNorm,
           "\033[1;34m trigger:\033[0m", trigger,
           "\033[1;34m rsi:\033[0m", rsi[-1],
           "\033[1;34m rsiSma:\033[0m", rsiSma[-1])
    if macNorm > trigger and rsi[-2] <= rsiSma[-2] and rsi[-1] > rsiSma[-1] and SMA13 < closeData[-1] and abs (
            closeData[-1] - SMA13) / SMA13 <= float (NmacdRsiRate) and (status is False or status is None):
        configData[symbolKey] = True
        signal = "NmacdeRsi做多"
    elif macNorm < trigger and rsi[-2] >= rsiSma[-2] and rsi[-1] < rsiSma[-1] and SMA13 > closeData[-1] and abs (
            closeData[-1] - SMA13) / SMA13 <= float (NmacdRsiRate) and (status is True or status is None):
        configData[symbolKey] = False
        signal = "NmacdeRsi做空"
    return signal


def job(timee, method=""):
    configData= loadConfig ("./config.json")
    symbols = configData['symbol']
    um_futures_client = UMFutures (proxies={'https': proxy})
    for sym in symbols:
        symbol = sym
        symbolKey = sym + timee + method
        try:
            status = configData[symbolKey]
        except:
            status = None
        try:
            data = um_futures_client.klines (symbol, timee)
        except Exception as e:
            print ("\033[1;31m " + repr (e) + "\033[0m")
            continue
        closeData = []
        for em in data:
            closeData.append (float (em[4]))
        if method == "vegas":
            signal = vegas (closeData, configData, status, symbolKey)
        elif method == "NmacdeRsi":
            signal = NmacdeRsi (closeData, configData, status, symbolKey)
        else:
            signal = EMA2155144 (closeData, configData, status, symbolKey)
        if signal is not None:
            sendMessage.bark (symbol, timee + "级别出现{}信号".format (signal), barkUrl,
                              barkKey)
            print (symbol + timee + "级别出现{}信号".format (signal))

        time.sleep (10)
    with open ("./config.json", "w") as f:
        json.dump (configData, f)


if not os.path.exists ("./config.json"):
    print ("config文件不存在，请创建")
configDataFirst = loadConfig ("./config.json")
try:
    barkUrl = configDataFirst['barkUrl']
    barkKey = configDataFirst['barkKey']
    proxy = configDataFirst['proxy']
    timee = configDataFirst['time']
except Exception as e:
    print ("\033[1;31m " + "找不到"+repr (e) + "\033[0m")
    os.system ('pause')
sendMessage.bark ("开始运行", "test", barkUrl, barkKey)
if "15m" in timee:
    schedule.every (5).minutes.do (job, timee="15m")
if "1h" in timee:
    schedule.every (20).minutes.do (job, timee="1h")
    schedule.every (20).minutes.do (job, timee="1h", method="NmacdeRsi")
    schedule.every (3).hours.do (job, timee="1h", method="vegas")
if "1d" in timee:
    schedule.every (4).hours.do (job, timee="1d")
# schedule.every (1).hours.do (job, timee="1h", method="NmacdeRsi")
print (schedule.get_jobs ())
schedule.run_all (delay_seconds=3)
while True:
    schedule.run_pending ()
    time.sleep (1)

