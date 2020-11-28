import aiohttp, urllib, os, re
from tools import updateCounter, searchResultsTest

# Searches youtube, taking a query and a result number as parameters
# and returning a url

async def search(query, n, prefix=None): 
    async with aiohttp.ClientSession() as session:
        async with session.get('http://www.youtube.com/results', params = {'q': query}) as r:
            if r.status != 200:
                raise RuntimeError(f'{r.status} - {r.reason}')
            source = await r.text()
            results = re.findall(r'"\/watch\?v=(.{11})', source)
            if searchResultsTest(results, n) != 0:
                return searchResultsTest(results, n)
            queryString = urllib.parse.urlencode({'v': results[n]})
            return f'http://www.youtube.com/watch?{queryString}'

async def getEmbed(results):
    return None
