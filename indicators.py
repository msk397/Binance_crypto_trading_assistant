def calculate_ema(prices, days, smoothing=2):
    '''
    author = "techno_gssb"
    totally eqv. to talib.EMA
    '''
    ema = []
    for _ in prices[1:days]:
        ema.append (float ("nan"))
    # ema = [sum(prices[:days]) / days]
    ema.append (sum (prices[:days]) / days)
    for price in prices[days:]:
        ema.append ((price * (smoothing / (1 + days))) + ema[-1] * (1 - (smoothing / (1 + days))))
    return ema


def WMA(x, y):
    wma = []
    norm = y * (y + 1) / 2
    for i in range (y, len (x)):
        summ = 0
        for j in range (0, y):
            summ += x[i - j] * (y - j)
        wma.append (summ / norm)
    return wma


def SMA(data, days=55):
    sma = []
    for i in range (days, len (data)):
        summ = 0
        for j in range (0, days):
            summ += data[i - j]
        sma.append (summ / days)
    return sma


def RMA(r, days, name=0):
    cps = [v[name] for v in r] if name else r
    rmas = [0 for i in range (len (cps))]  # 创造一个和cps一样大小的集合
    alpha = 1 / days

    for i in range (len (cps)):
        if i < days - 1:
            rmas[i] = 0
        else:
            if rmas[i - 1]:
                rmas[i] = alpha * cps[i] + (1 - alpha) * rmas[i - 1]
            else:
                ma = 0
                for i2 in range (i - days, i):  # 求平均值
                    ma += cps[i2 + 1]
                rmas[i] = ma / days
    return rmas


def RSI(data, days=21):
    loss = [0]
    maxloss = []
    minloss = []
    rsi = []
    sma = []
    for i in range (1, len (data)):
        loss.append (data[i] - data[i - 1])
        maxloss.append (max (loss[-1], 0))
        minloss.append (-min (loss[-1], 0))
        up = RMA (maxloss, 21)[-1]
        down = RMA (minloss, 21)[-1]
        # rsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))
        if down == 0:
            rsi.append (100)
        elif up == 0:
            rsi.append (0)
        else:
            rsi.append (100 - (100 / (1 + up / down)))
        sma.append (SMA (rsi))
    return rsi, sma[-1]


def normalizeMacd(data, sma=13, lma=21, np=50, tsp=9):
    fastMa = calculate_ema (data, sma)
    slowMa = calculate_ema (data, lma)
    ratio = []
    mac = []
    macNorm = []
    trigger = []
    lens = len (fastMa)
    for i in range (0, lens):
        ratio.append (min (slowMa[i], fastMa[i]) / max (slowMa[i], fastMa[i]))
        if fastMa[i] > slowMa[i]:
            mac.append (2 - ratio[i] - 1)
        else:
            mac.append (ratio[i] - 1)
        macNorm.append ((((mac[i] - min (mac[-np:])) / (max (mac[-np:]) - min (mac[-np:]) + 0.000001) * 2) - 1))
        trigger.append (WMA (macNorm, tsp))
    return macNorm[-1], trigger[-1][-1]