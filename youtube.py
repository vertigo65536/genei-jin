import aiohttp, urllib, os, re
from tools import updateCounter

# Searches youtube, taking a query and a result number as parameters
# and returning a url

async def search(query, n): 
    async with aiohttp.ClientSession() as session:
        async with session.get('http://www.youtube.com/results', params = {'q': query}) as r:
            if r.status != 200:
                raise RuntimeError(f'{r.status} - {r.reason}')
            source = await r.text()
            results = re.findall(r'"\/watch\?v=(.{11})', source)
            if len(results) <= 0:
                return -1
            if len(results) < n:
                return -2
            queryString = urllib.parse.urlencode({'v': results[n]})
            return f'http://www.youtube.com/watch?{queryString}'

# Edits the result number of an already searched youtube video
# takes the original message, the query message and the operation as 
# param

async def increment(ytMessage, message, operation, db):
    if operation == "+":
        newCounter = int(ytMessage[3])+1
    elif operation =="-":
        newCounter = int(ytMessage[3])-1
        if newCounter < 0:
            newCounter = 0 
    else:
        newCounter = 0 
    newUrl = await search(ytMessage[2], newCounter)
    await message.edit(content=newUrl)
    updateCounter(message.id, db, newCounter)
    return
