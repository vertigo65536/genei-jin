from tools import updateCounter, searchResultsTest
import requests, os, json
from dotenv import load_dotenv
from bs4 import BeautifulSoup

# Searches youtube, taking a query and a result number as parameters
# and returning a url

baseUrl = "https://scene.djwt.xyz/"


async def search(query, n, prefix=None):
    load_dotenv()
    TOKEN = os.getenv('SCENE_TOKEN')
    baseUrl = "https://scene.djwt.xyz/"
    #baseUrl = "http://localhost:8000/"
    url = baseUrl + "api/quote/" + query
    headers = {
        'User-Agent':       'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
        'Authorization':    "Api-Key " + TOKEN,
        'Connection':       "keep-alive",
        "Accept":           "*/*",
        "Referer":          baseUrl
    }
    with requests.Session() as session:
        session.get(baseUrl, headers=headers)
        response = requests.get(url, headers=headers)
        responseJson = response.json()
        while n >= len(responseJson):
            n = n - len(responseJson)
        selectedQuote = responseJson[n]
        headers['Referer'] = baseUrl + "?q="+str(selectedQuote['quote_id'])+"&t=c&show=all"
        #headers['X-CSRFToken'] = session.cookies['csrftoken']
        params = {
            'q':        selectedQuote['quote_id'],
            't':        'c',
            "show":     "all",
        }
        clip = session.post(baseUrl + "genclip/", data=params, headers=headers, cookies=session.cookies)
        clipMarkup = clip.text
        soup = BeautifulSoup(clipMarkup, 'html')
        return soup.find('video')['src']

async def getEmbed(results, colour):
    return None
