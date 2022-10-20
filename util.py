import json
import time


def getTime():
    nowTime = time.strftime ('%Y-%m-%d %H:%M:%S', time.localtime (time.time ()))
    return nowTime


def loadConfig(filePath):
    with open (filePath, 'r',encoding='utf-8') as fcc_file:
        configData = json.load (fcc_file)
    return configData
