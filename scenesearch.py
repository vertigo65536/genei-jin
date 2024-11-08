from tools import updateCounter, searchResultsTest
import requests, os, json
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Searches youtube, taking a query and a result number as parameters
# and returning a url

baseUrl = "https://scene.djwt.xyz/"


async def search(query, n, prefix=None, modifier=None):
    show = getShow(prefix)
    load_dotenv()
    TOKEN = os.getenv('SCENE_TOKEN')
    baseUrl = "https://scene.djwt.xyz/"
    if show == None:
        url = baseUrl + "api/quote/" + query
    else:
        url = baseUrl + "api/quote/" + show + "/" + query
    headers = {
        'User-Agent':       'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Authorization':    "Api-Key " + TOKEN,
        'Connection':       "keep-alive",
        "Accept":           "*/*",
        "Referer":          baseUrl
    }
    print(url)
    with requests.Session() as session:
        session.get(baseUrl, headers=headers)
        response = requests.get(url, headers=headers)
        responseJson = response.json()
        try:
            if responseJson['res'] == "Object matching quote does not exists":
                return "No matches"
        except:
            pass
        while n >= len(responseJson):
            n = n - len(responseJson)
        selectedQuote = responseJson[n]
        headers['Referer'] = baseUrl + "?q="+str(selectedQuote['quote_id'])+"&t=c&show=all"
        t = "c"
        if modifier == "+":
            t = "s"
        if modifier == "-":
            t = "e"
        if modifier == "=":
            t = "c"
        if modifier == ".":
            t = "j"
        params = {
            'q':        selectedQuote['quote_id'],
            't':        t,
            "show":     "all",
        }
        clip = session.post(baseUrl + "genclip/", data=params, headers=headers, cookies=session.cookies)
        clipMarkup = clip.text
        soup = BeautifulSoup(clipMarkup, 'html')
        return soup.find('video')['src']

async def getEmbed(results, colour):
    return None

def getShow(prefix):
    print(prefix)
    if "sunny" in prefix:
        return "It's Always Sunny in Philadelphia"
    if "avgn" in prefix:
        return "Angry Video Game Nerd"
    if "sp" in prefix:
        return "South Park"
    if "pp" in prefix:
        return "Pure Pwnage"
    if "sb" in prefix:
        return "Spongebob Squarepants"
    else:
        return None

