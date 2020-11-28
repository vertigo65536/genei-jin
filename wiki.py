import os, wikipedia
from tools import updateCounter, searchResultsTest

# Searches wikipedia and returns a url, taking a message and result number
# as values

async def search(message, n, prefix=None):
    search = wikipedia.search(message)
    if searchResultsTest(search, n) != 0:
        return searchResultsTest(search, n)
    nthSearch = search[n]
    try:
        page = wikipedia.page(str(nthSearch), auto_suggest=0).url
    except wikipedia.DisambiguationError as e:
        page = "https://en.wikipedia.org/wiki/" + str(nthSearch)
    return page

async def getEmbed(results):
    return None
