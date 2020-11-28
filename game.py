import aiohttp, urllib, os, re, requests, discord
from bs4 import BeautifulSoup
from tools import updateCounter
from currency_converter import CurrencyConverter

# Searches youtube, taking a query and a result number as parameters
# and returning a url

async def search(query, n, prefix=None):
    queryString = urllib.parse.quote_plus(query)
    queryString = queryString.replace("%20", "+")
    url = 'https://www.pricecharting.com/search-products?q="' + queryString + '"&type=prices'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, features='html.parser')
    if soup.find(id="games_table"):
        values = scrapeFromSearch(soup.find(id="games_table"))
    else:
        values = scrapeFromPage(soup, page.url)
    if values == -1 or n >= len(values):
        return -1
    else:
        return values[n]

# Edits the result number of an already searched youtube video
# takes the original message, the query message and the operation as 
# param

async def increment(gameMessage, message, operation, db):
    if operation == "+":
        newCounter = int(gameMessage[3])+1
    elif operation =="-":
        newCounter = int(gameMessage[3])-1
        if newCounter < 0:
            newCounter = 0 
    else:
        newCounter = 0
    results = await search(gameMessage[2], newCounter)
    if results == -1:
        return
    for key, values in results.items():
        e = discord.Embed(title=key)
        for value in values:
            cover = getImageUrl(value['link'])
            e.set_thumbnail(url=cover)
            e.add_field(
                name = value['console'],
                value = getFormattedRow(value),  
                inline = False
            )
    await message.edit(embed = e)
    updateCounter(message.id, db, newCounter)
    return

def scrapeFromSearch(soup):
    values = []
    lastName = ""
    for rows in soup.findAll('tr'):
        temp = {}
        for cols in rows.findAll('td'):
            classList = cols.get('class')
            if cols.find('a'):
                if cols.find('a').find('span'):
                    temp[classList[len(classList) - 1]] = cols.find('a').find('span').string.strip()
                else: 
                    temp[classList[len(classList) - 1]] = cols.find('a').string.strip()
                    temp['link'] = cols.find('a')['href']
            elif cols.find('span'):
                temp[classList[len(classList) - 1]] = cols.find('span').string
            else:
                temp[classList[len(classList) - 1]] = cols.string.strip()
        if len(temp) < 1:
            continue
        if temp['title'] != lastName:
            values.append({temp['title']:[]})
            lastName = temp['title']
            del temp['title']
            del temp['add_to']
            values[len(values)-1][lastName].append(temp)
        else:
            del temp['title']
            del temp['add_to']
            values[len(values)-1][lastName].append(temp)
    return values


def scrapeFromPage(soup, url):
    try:
        temp = soup.find(id="product_name").getText().split("\n")
    except:
        return -1
    names = []
    for i in range(len(temp) - 1):
        if temp[i].isspace() == True or not temp[i] or temp[i] == '':
            continue
        names.append(temp[i].strip())
    try:
        used = soup.find(id="used_price").find("span").getText().strip()
        cib = soup.find(id="complete_price").find("span").getText().strip()
        new = soup.find(id="new_price").find("span").getText().strip()
    except:
        return -1
    value = [{names[0]:[{'console':names[1],
                          'used_price':used,
                          'cib_price':cib,
                          'new_price':new,
                          'link':url
                          }]}]
    return value

def getImageUrl(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, features='html.parser')
    for links in soup.findAll("div", {"class": "cover"}):
        return links.find('img')['src']

def getFormattedRow(value):
    string = "Loose: "
    if value['used_price'] == "" or value['used_price'] == None:
        string = string + "Unknown\nCIB: "
    else:
        string = string + parseDollar(value['used_price']) + "\nCIB: "
    if value['cib_price'] == "" or value['cib_price'] == None:
        string = string + "Unknown\nNew: "
    else:
        string = string + parseDollar(value['cib_price']) + "\nNew: "
    if value['new_price'] == "" or value['new_price'] == None or value['new_price'] == "N/A":
        string = string + "Unknown or N/A"
    else:
        string = string + parseDollar(value['new_price'])
    return string
    
def parseDollar(dollar):
    return "£" + str("%.2f" % round(CurrencyConverter()    .convert(dollar[1:], 'USD', 'GBP'), 2))

async def getEmbed(results):
    if results == -1:
        return None
    for key, values in results.items():
        e = discord.Embed(title=key)
        for value in values:
            cover = getImageUrl(value['link'])
            e.set_thumbnail(url=cover)
            e.add_field(
                name = value['console'],
                value = getFormattedRow(value),
                inline=False
            )
    return e
