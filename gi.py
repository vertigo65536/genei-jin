import discord, os, urllib.request as urllib2
from google_images_download import google_images_download
from tools import updateCounter


# Search google images, taking a query and a result number as a parameter
# and returning a URL

def search(message, n):
    response = google_images_download.googleimagesdownload()
    #content = tools.getMessageContent(message.content)
    message = message.encode('utf-8').decode('raw_unicode_escape', 'ignore')
    arguments = {"keywords": message,
                 "limit":n,
                 "offset":n-1,
                 "no_download":True}
    try:
        response = response.download(arguments)
    except SystemExit:
        return -1
    return response[0][message][len(response[0][message]) - 1]


# Updates a search to a new result number, taking the original search
# message, the query message, and the operation as parameters

async def increment(giMessage, message, operation, db):
    if operation == "+":
        newCounter = int(giMessage[3])+1
    elif operation == "-":
        newCounter = int(giMessage[3])-1
        if newCounter < 0:
            newCounter = 0
    else:
        newCounter = 0
    newUrl = search(giMessage[2], newCounter)
    while checkValidImageUrl(newUrl) == 0:
        if newCounter == 0:
            return
        if operation == "+":
            newCounter = newCounter+1
        elif operation == "-":
            newCounter = newCounter-1
        newUrl = search(giMessage[2], newCounter)
    e = discord.Embed()
    e.set_image(url=newUrl)
    await message.edit(embed=e)
    updateCounter(message.id, db, newCounter)
    return

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
