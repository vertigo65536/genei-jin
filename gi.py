import discord, os, urllib.request as urllib2, requests, urllib, re, json, urllib.parse as urlparse
from bs4 import BeautifulSoup
#from google_images_download import google_images_download
from tools import updateCounter

# Search google images, taking a query and a result number as a parameter
# and returning a URL

async def search(message, n, prefix=None):
    if n < 0:
        return 40
    elif n > 40:
        return -2
    counter = 0
    while True:
        link = getNthBingImage(message, n)
        print(checkValidImageUrl(link))
        if checkValidImageUrl(link) == 0:
            n = n+1
        else:
            return link
    return link

async def getEmbed(results, colour):
    e = discord.Embed(colour=colour)
    e.set_image(url=results)
    return e

def getNthBingImage(query, n):
    headers = {
        "Referer": "http://www.bing.com/",
        "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Cookie": "ipv6=hit=1617439166393&t=4; MMCA=ID=649A1DE6148C48D98D43BA736DEB1A28; _IDET=MIExp=0; MUID=1528F57D4102646F28DFE57340616513; MUIDB=1528F57D4102646F28DFE57340616513; _EDGE_S=F=1&SID=2A8CE1ACD25C65902E72F1A2D33F647B&mkt=en-gb&ui=en-gb; _EDGE_V=1; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=760A6FBE495945698ED26CA26170F843&dmnchg=1; SRCHUSR=DOB=20210403&T=1617435561000; SRCHHPGUSR=SRCHLANGV2=en&BRW=NOTP&BRH=S&CW=1177&CH=693&DPR=1&UTC=60&DM=0&HV=1617435786&WTS=63753032361&ADLT=OFF; _SS=SID=2A8CE1ACD25C65902E72F1A2D33F647B&R=60&RB=0&GB=0&RG=200&RP=55; _HPVN=CS=eyJQbiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMS0wNC0wM1QwMDowMDowMFoiLCJJb3RkIjowLCJEZnQiOm51bGwsIk12cyI6MCwiRmx0IjowLCJJbXAiOjF9; _RwBf=mtu=0&g=0&cid=&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2021-04-03T07:43:05.4474584+00:00; imgv=lodlg=1&gts=20210403&gt=1; BCP=AD=1&AL=1&SM=1"
        }
    var = requests.get(r'https://www.bing.com/images/search?q=' + urllib.parse.quote(query) + "&adlt=off", headers = headers, allow_redirects=True)
    soup = BeautifulSoup(var.text, features='html.parser')
    imageArray = []
    imageLinks = []
    for ul in soup.findAll('ul'):
        for li in ul.findAll('li'):
            for a in li.findAll('a', {'class': 'iusc'}):
                imageLinks.append('http://bing.com' + a['href'])
                continue
    parsed = urlparse.urlparse(imageLinks[n]) 
    print(urlparse.parse_qs(parsed.query)['mediaurl'][0])
    return urlparse.parse_qs(parsed.query)['mediaurl'][0]

def checkValidImageUrl(url):
    var = requests.get(url)
    print(var.status_code)
    if var.status_code == 200:
        return 1
    else:
        return 0
    #req = urllib2.Request(url)
    #try:
    #    resp = urllib2.urlopen(req)
    #except urllib2.HTTPError as e:
    #    return 0
    #except urllib2.URLError as e:
    #    return 0
    #else:
    #    return 1
