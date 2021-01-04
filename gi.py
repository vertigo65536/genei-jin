import discord, os, urllib.request as urllib2, requests, urllib, re, json
from bs4 import BeautifulSoup
from google_images_download import google_images_download
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
        if checkValidImageUrl(link) == 0:
            n = n+1
        else:
            return link
    return link

async def getEmbed(results):
    e = discord.Embed()
    e.set_image(url=results)
    return e

def getNthBingImage(query, n):
    headers = {
        "Referer": "http://www.bing.com/",
        "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Cookie": "MMCA=ID=333F3524EFB54F8082102CB4BFCEC657; _IDET=MIExp=0&VSNoti2=20210104; ipv6=hit=1609785124246&t=6; _EDGE_S=mkt=en-gb&ui=en-gb&F=1&SID=00AAA669AA69616D1E96A9DCAB9260D8; _EDGE_V=1; MUID=0B74C38A9D996E232D50CC3F9C626FBD; SRCHD=AF=NOFORM; SRCHUID=V=2&GUID=462795EBAA544C01AEC60CD5031BC994&dmnchg=1; SRCHUSR=DOB=20210104&T=1609781513000; _SS=SID=00AAA669AA69616D1E96A9DCAB9260D8&R=60&RB=0&GB=0&RG=200&RP=55; _HPVN=CS=eyJQbiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiUCJ9LCJTYyI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiSCJ9LCJReiI6eyJDbiI6MSwiU3QiOjAsIlFzIjowLCJQcm9kIjoiVCJ9LCJBcCI6dHJ1ZSwiTXV0ZSI6dHJ1ZSwiTGFkIjoiMjAyMS0wMS0wNFQwMDowMDowMFoiLCJJb3RkIjowLCJEZnQiOm51bGwsIk12cyI6MCwiRmx0IjowLCJJbXAiOjEwfQ==; MUIDB=0B74C38A9D996E232D50CC3F9C626FBD; SRCHHPGUSR=CW=683&CH=693&DPR=1&UTC=0&DM=0&HV=1609783266&WTS=63745378313; _RwBf=mtu=0&g=0&cid=&o=2&p=&c=&t=0&s=0001-01-01T00:00:00.0000000+00:00&ts=2021-01-04T18:02:26.8154153+00:00; ipv6=hit=1609778938708&t=6; _ITAB=STAB=TR; BCP=AD=1&AL=1&SM=1"
    }
    var = requests.get(r'https://www.bing.com/images/search?q=' + urllib.parse.quote(query), headers = headers, allow_redirects=True)
    soup = BeautifulSoup(var.text, features='html.parser')
    imageArray = []
    for ul in soup.findAll('ul'):
        for li in ul.findAll('li'):
            for img in li.findAll('img'):
                possibleNames = ['src', 'data-src']
                key = None
                for i in range(len(possibleNames)):
                    try:
                        img[possibleNames[i]]
                        key = possibleNames[i]
                    except:
                        pass
                if key == None:
                    continue
                if img[key][0:4] == 'http':
                    tmp = img[key].split('?')
                    imageArray.append(tmp[0])
    return imageArray[n]

def checkValidImageUrl(url):
    req = urllib2.Request(url)
    try:
        resp = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        return 0
    except urllib2.URLError as e:
        return 0
    else:
        return 1
