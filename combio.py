import os, combio_api, discord
from tools import updateCounter, searchResultsTest

# Searches combio, returning a video url. Takes query and result number 
# as params

async def search(message, n, prefix):
    method = getGenType(prefix)
    result = combio_api.search(message)
    if searchResultsTest(result, n) != 0:
        return searchResultsTest(result, n)
    result = result[n][1]
    if method == 0:
        ts = combio_api.getDefaultTimestamps(result)
    elif method == 1:
        timestamps = combio_api.getAllTimestamps(result)
        endstamp = timestamps[len(timestamps) - 2]['ts2']
        for i in range(len(timestamps)):
            startstamp = timestamps[len(timestamps) - i -2]['ts1']
            if (int(endstamp) - int(startstamp) > 20000):
                startstamp = timestamps[len(timestamps) - i - 1]['ts1']
                break;
        ts = {'ts1': startstamp,
              'ts2': endstamp}
    elif method == 2:
        timestamps = combio_api.getAllTimestamps(result)
        startstamp = timestamps[2]['ts1']
        for i in range(len(timestamps)):
            endstamp = timestamps[i]['ts2']
            if (int(endstamp) - int(startstamp) > 20000):
                endstamp = timestamps[i - 1]['ts2']
                break;
        ts = {'ts1': startstamp,
              'ts2': endstamp}
    elif method == 3:
        timestamps = combio_api.getAllTimestamps(result)
        startstamp = timestamps[len(timestamps)//2]['ts1']
        for i in range(len(timestamps)//2):
            teststamp = timestamps[len(timestamps)//2 - i]['ts1']
            if int(startstamp) - int(teststamp) > 10000:
                startstamp = timestamps[len(timestamps)//2 - (i - 1)]['ts1']
                key = i - 1
                break;
        for i in range(len(timestamps)):
            endstamp = timestamps[key + i]['ts2']
            if (int(endstamp) - int(startstamp) > 20000):
                endstamp = timestamps[key + i - 1]['ts2']
                break; 
        ts = {'ts1': startstamp,
              'ts2': endstamp}
    else:
        return -1
    return combio_api.getVideoUrl(result, ts)

async def getEmbed(results):
    return None

def getGenType(prefix):
    genType = 0
    if prefix == "%co+":
        genType = 1
    if prefix == "%co-":
        genType = 2
    if prefix == "%co=":
        genType = 3
    return genType
