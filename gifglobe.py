import requests, json, discord
from tools import updateCounter, searchResultsTest
from bs4 import BeautifulSoup

# Searches youtube, taking a query and a result number as parameters
# and returning a url

timeout = 30

async def search(query, n, prefix=None):
    baseurl = '.gifglobe.com/'
    protocol = 'https://'
    if prefix in ['%ft', '%fatherted']:
        url = protocol + 'fatherted' + baseurl
    elif prefix in ['%mb', '%mightyboosh']:
        url = protocol + 'mightyboosh' + baseurl
    elif prefix in ['%dt', '%daytoday']:
        url = protocol + 'thedaytoday' + baseurl
    elif prefix in ['%bb', '%blackbooks']:
        url = protocol + 'blackbooks' + baseurl
    elif prefix in ['%ap', '%alanpartridge']:
        url = protocol + 'partridge.cloud/'
    elif prefix in ['%ps', '%peepshow']:
        url = protocol + 'peepshow' + baseurl
    elif prefix in ['%office']:
        url = protocol + 'brent.cloud/'
    elif prefix in ['%toi', '%thickofit']:
        url = protocol + 'thethickofit' + baseurl
    urlList = getSearchResultsList(query, url)
    sceneData = getSceneData(urlList[n])
    print(sceneData)
    return sceneData


def getSearchResultsList(query, url):
    print (url.replace('https://', ''))
    r = requests.post(                                                                                           
        url=url + '/inc/quote-finder.php',
        data={
            'str': query
        },
        headers={
            'Host': url.replace('https://', '')[:-1],
            'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Length': str(len(query)),
            'Origin': url,
            'Connection': 'keep-alive',
            'Referer': url,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers'
        },
        timeout=timeout
        )
    soup = BeautifulSoup(r.text, features='html.parser')
    links = []
    for link in soup.findAll('div', {'class': 'search-result'}):
        links.append(url + '/' + link.find('a')['href'])
    return links

def getSceneData(url):
    r = requests.post(
        url = url,
        timeout = timeout
    )
    soup = BeautifulSoup(r.text, features='html.parser')
    for container in soup.findAll('div', {'class': 'container scene'}):
        episode = container.find('h2').getText()
        break
    imageLink = soup.find('img', {'class': 'img-responsive'})['src']
    return {'image': imageLink, 'episode': episode}

async def getEmbed(results, colour):
    if results == -1:
        return None
    e = discord.Embed(title=results['episode'], colour=colour)
    e.set_image(url=results['image'])
    return e
