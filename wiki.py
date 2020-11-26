import os, wikipedia
from tools import updateCounter

# Searches wikipedia and returns a url, taking a message and result number
# as values

async def search(message, n, prefix=None):
    search = wikipedia.search(message)
    if len(search) == 0:
        return -1
    if n >= len(search):
        n = n - (len(search) * int((float(n) / len(search))))
    nthSearch = search[n]
    try:
        page = wikipedia.page(str(nthSearch), auto_suggest=0).url
    except wikipedia.DisambiguationError as e:
        page = "https://en.wikipedia.org/wiki/" + str(nthSearch)
    return page

# Increments an existing search result message, taking the query message,
# the result message and the operation as params

async def getEmbed(results):
    return None

async def increment(wikiMessage, message, operation, db):
    if operation == "+":
        newCounter = int(wikiMessage[3])+1
    elif operation == "-":
        newCounter = int(wikiMessage[3])-1
        if newCounter < 0:
            newCounter = 0
    else:
        newCounter = 0
    newUrl = await search(wikiMessage[2], newCounter)
    await message.edit(content=newUrl)
    updateCounter(message.id, db, newCounter)
    return
