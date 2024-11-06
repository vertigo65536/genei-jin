import os, requests, urllib, discord, numpy
from math import ceil
from tools import updateCounter, searchResultsTest
from bs4 import BeautifulSoup

# Searches wikipedia and returns a url, taking a message and result number
# as values

async def search(message, n, prefix=None, modifier=None):
    try:
        baseUrl = "https://www.dictionary.com"
        url = baseUrl + "/browse/" + urllib.parse.quote(message)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, features='html.parser')

        for suggestion in soup.findAll("h2", {"class": "spell-suggestions-subtitle"}):
            page = requests.get(baseUrl + suggestion.find('a')['href'])
            soup = BeautifulSoup(page.text, features='html.parser')

        definitionBlock = soup.find('div', {'class': 'e16867sm0'})
        wordInfo = {}
        wordInfo['url'] = url
        wordInfo['title'] = soup.find('h1').getText()
        wordInfo['pronunciation'] = soup.find('span', {'class': 'pron-spell-content'}).getText()
        for definition in definitionBlock.findAll('section', {'class': 'e1hk9ate4'}):
            definitionType = definition.find('h3').getText().strip().rstrip() 
            wordInfo[definitionType] = []
            for defInstance in definition.findAll('span', {'class': 'one-click-content'}):
                tmpArray = []
                tmpArray.append(defInstance.getText())
                try:
                    tmpArray.append(defInstance.find('span').getText().rstrip().strip())
                    tmpArray[0] = tmpArray[0].replace(tmpArray[1], "").rstrip().strip()
                except:
                    pass
                wordInfo[definitionType].append(tmpArray)

        # 'e1q3nk1v3'
        return wordInfo
    except:
        return -1

async def getEmbed(results, colour):
    if results == -1:
        return None
    e = discord.Embed(
        title=results['title'],
        url=results['url'],
        description=results['pronunciation'],
        colour=colour
    )
    for key, values in results.items():
        if key not in ['title', 'url', 'pronunciation']:
            string = ""
            for i in range(len(values)):
                string = string + "• " + values[i][0] + "\n"
                try:
                    string = string + "\n*" + values[i][1] + "*\n"
                except:
                    pass
            string = string.rstrip()
            if len(string) >= 1024:
                division = ceil(len(string)/1024)
                stringSplit = numpy.array_split(string.split("\n•"), division)
                for i in range(len(stringSplit)):
                    stringSplit[i] = "\n•".join(stringSplit[i])
                string = stringSplit
            else:
                string = [string]
            for i in range(len(string)):
                e.add_field(
                    name=key,
                    value=string[i],
                    inline=False
                )
    
    return e
