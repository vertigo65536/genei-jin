import os, combio_api
from tools import updateCounter

# Searches combio, returning a video url. Takes query and result number 
# as params

def search(message, n, method = 0):
    result = combio_api.search(message)
    if result == -1:
        return -1
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
        startstamp = timestamps[0]['ts1']
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

# Edits an existing search result message, taking the query message, 
# search result message and operation as params

async def increment(coMessage, message, operation, db, genType):
    if operation == "+":
        newCounter = int(coMessage[3])+1
    elif operation =="-":
        newCounter = int(coMessage[3])-1
        if newCounter < 0:
            newCounter = 0
    else:
        newCounter = 0
    newUrl = search(coMessage[2], newCounter, genType)
    await message.edit(content=newUrl)
    updateCounter(message.id, db, newCounter)
    return
