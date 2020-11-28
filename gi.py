import discord, os, urllib.request as urllib2
from google_images_download import google_images_download
from tools import updateCounter


# Search google images, taking a query and a result number as a parameter
# and returning a URL

async def search(message, n, prefix=None):
    if n < 0:
        return 25
    elif n > 25:
        return -2
    counter = 0
    while True:
        response = google_images_download.googleimagesdownload()
        if counter >= 26:
            return -2
        message = message.encode('utf-8').decode('raw_unicode_escape', 'ignore')
        arguments = {"keywords": message,
                    "limit":n,
                    "offset":n-1,
                    "no_download":True}
        try:
            response = response.download(arguments)
        except SystemExit:
            return -1
        link = response[0][message][len(response[0][message]) - 1]
        if checkValidImageUrl(link) == 1:
            break
        counter = counter+1
    return link

async def getEmbed(results):
    e = discord.Embed()
    e.set_image(url=results)
    return e

# Checks if a url returned above returns an error

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
