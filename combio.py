import os, combio_api
from tools import updateCounter

# Searches combio, returning a video url. Takes query and result number 
# as params

def search(message, n):
    result = combio_api.search(message)
    if result == -1:
        return -1
    result = result[n][1]
    ts = combio_api.getDefaultTimestamps(result)
    return combio_api.getVideoUrl(result, ts)

# Edits an existing search result message, taking the query message, 
# search result message and operation as params

async def increment(coMessage, message, operation):
    if operation == "+":
        newCounter = int(coMessage[3])+1
    elif operation =="-":
        newCounter = int(coMessage[3])-1
        if newCounter < 0:
            newCounter = 0
    else:
        newCounter = 0
    newUrl = search(coMessage[2], newCounter)
    await message.edit(content=newUrl)
    updateCounter(message.id, getDatabase(), newCounter)
    return

# Returns the database url of combio result messages

def getDatabase():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "co.csv")
