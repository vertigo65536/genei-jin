import os
import re
import requests
import discord
import json
import urllib.parse
import wikipedia
import random
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import you
import csv
from google_images_download import google_images_download
from bs4 import BeautifulSoup
from dotenv import load_dotenv


async def addSelectionArrows(message):
    await message.add_reaction("⏪")
    await message.add_reaction("⏩")

def getMessagePrefix(message):
    return message.split()[0]

def getMessageContent(message):
    split = message.split()
    content = ""
    if len(split) <= 1:
        return -1
    else:
        for i in range(len(split)-1):
            if i == 0:
                content = split[i+1]
            else:
                content = content + " " + split[i+1]
    return content


def getNthYtVid(query, pageToken):
    api_service_name = "youtube"
    api_version = "v3"    
    
    developerKey = os.getenv("YOUTUBE_API_KEY")
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=developerKey)

    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        order="relevance",
        pageToken=pageToken,
        q=query,
        type="video"
    )
    
    response = request.execute()
    return response

def ytSearch(message):
    response = getNthYtVid(message, "")
    id = response['items'][0]['id']['videoId']
    return "https://www.youtube.com/watch?v=" + id

def giNthSearch(message, n):
    response = google_images_download.googleimagesdownload()
    content = getMessageContent(message.content)
    arguments = {"keywords": content,
                 "limit":n,
                 "offset":n-1,
                 "no_download":True}
    response = response.download(arguments)
    return response[0][content][len(response[0][content]) - 1]
    
async def giSearch(message):
    imgUrl = giNthSearch(message, 1)
    print(imgUrl)
    e = discord.Embed()
    e.set_image(url=imgUrl)
    await message.channel.send("", embed=e)
    return

def combQuote(message):
    ##query comb.io, and retrieve link for the first result
    r = requests.post(
        url='https://comb.io/a/q',
        data={
            'q': message
        },
        headers={
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-length': '3',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://comb.io',
            'referer': 'https://comb.io/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        })
    markup = json.loads(r.text[1:])
    soup = BeautifulSoup(markup['payload']['markup'][0], features='html.parser')
    for link in soup.findAll('a'):
        href = link.get('href')
        break
    largeID = href.split('/')[2]
    episodeID = largeID.split('?')[0]
    timestamp = largeID.split('?')[1][4:]
    
    
    
    ##retrieve video start and finish time stamps
    page = requests.get('https://comb.io' + href)
    soup = BeautifulSoup(page.text, features='html.parser')
    soup = soup.find(id="s")
    ts = []
    for timestamp in soup.findAll('input'):
        ts.append(timestamp['value'])
    
    data = {'media': episodeID}
    data['ts1'] = ts[0]
    data['ts2'] = ts[len(ts)-1]
    
    
    ##generate video from link
    r = requests.post(
        url='https://comb.io/create-clip',
        data=data,
        headers={
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en-US,en;q=0.9',
            'content-length': '80',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://comb.io',
            'referer': 'https://comb.io'+href,
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        })
    soup = BeautifulSoup(r.text, features='html.parser')
    for link in soup.findAll('source'):
        href = link.get('src')
    
    return href

def isLoneEmoji(message):
    pattern = re.compile('<:\w*:\d*>$')
    if pattern.match(message.content) and not message.attachments:
        return 1
    else:
        return 0

def getUserColour(message):
    bestColour = "#000000"
    bestRank = 0
    for role in message.author.roles:
        if role.position > bestRank and str(role.colour) != "#000000":
            bestColour = role.colour
    return bestColour

async def bigmoji(message):
    id = message.content[1:-1].split(':')[2]
    imageUrl = "https://cdn.discordapp.com/emojis/" + id
    e = discord.Embed(colour=getUserColour(message))
    e.set_image(url=imageUrl)
    await message.channel.send("", embed=e)
    await message.delete()
    return

async def setTitle(message):
    newTitle = name=getMessageContent(message.content)
    await message.guild.edit(name=newTitle)
    return
    
async def setChannelTitle(message):
    newTitle = getMessageContent(message.content)
    await message.channel.edit(name=str(newTitle))
    return
    
async def setTopic(message):
    newTopic = getMessageContent(message.content)
    await message.channel.edit(topic=str(newTopic))
    return
    
def getManPage():
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "man.txt"), "r")
    if f.mode == "r":
        return f.read()
    print("Failed to open man file")
    return

def getStoredWikiCounter(id):
    with open(WIKI_DATABASE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if row[0] == str(id):
                return row
        return -1
        
def updateWikiCounter(id, newN):
    with open(WIKI_DATABASE) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        rows = list(csv_reader)
        for i in range(len(rows)):
            if rows[i-1][0] == str(id):
                rows[i-1][2] = newN
    with open(WIKI_DATABASE, 'w', newline='\n', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(list(rows))
    return

def wikiSearch(message, n):
    search = wikipedia.search(message)
    if n >= len(search):
        n = n - (len(search) * int((float(n) / len(search))))
    nthSearch = search[n]
    try:
        page = wikipedia.page(str(nthSearch), auto_suggest=0).url
    except wikipedia.DisambiguationError as e:
        page = "https://en.wikipedia.org/wiki/" + str(nthSearch)
    return page

async def incrementWiki(wikiMessage, message, operation):
    if operation == "+":
        newCounter = int(wikiMessage[2])+1
    else:
        newCounter = int(wikiMessage[2])-1
        if newCounter < 0:
            newCounter = 0
    newUrl = wikiSearch(wikiMessage[1], newCounter)
    await message.edit(content=newUrl)
    updateWikiCounter(message.id, newCounter)
    return
    
async def createWikiPost(message):
    n = 0
    content = getMessageContent(message.content)
    url = wikiSearch(content, n)
    createdMessage = await message.channel.send(url)
    f = open(WIKI_DATABASE, 'a')
    f.write(str(createdMessage.id) + "," + str(content) + "," + str(n) + "\n")
    f.close()
    await addSelectionArrows(createdMessage)
    return

async def handleMessage(message):
    prefix = getMessagePrefix(message.content)
    content = getMessageContent(message.content)
    if prefix == "%ping":
        return "pong"
    elif prefix == "%co":
        return combQuote(content)
    elif isLoneEmoji(message):
        return await bigmoji(message)
    elif prefix == "%wiki":
        return await createWikiPost(message)
    elif prefix == "%yt":
        return ytSearch(content)
    elif prefix == "%gi":
        return await giSearch(message)
    elif prefix == "%title":
        return await setTitle(message)
    elif prefix == "%ctitle":
        return await setChannelTitle(message)
    elif prefix == "%topic":
        return await setTopic(message)
    elif prefix == "%man" or prefix == "%help":
        return getManPage()
    elif prefix == "%data":
        m1 = await message.channel.send(str(message))
        await addSelectionArrows(m1)
    return
    

async def handleEdit(message, operation):
    wikiMessage = getStoredWikiCounter(message.id)
    if wikiMessage != -1:
        await incrementWiki(wikiMessage, message, operation)

def initDatabases():
    open(YOUTUBE_DATABASE, 'w').close()
    open(WIKI_DATABASE, 'w').close()
    open(GI_DATABASE, 'w').close()
    return
    

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

YOUTUBE_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube.csv")
WIKI_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki.csv")
GI_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gi.csv")

initDatabases()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    
@client.event    
async def on_message(message):
    if message.author == client.user:
        return
    response = await handleMessage(message)
    if response != None:
        await message.channel.send(response)
    else:
        return

@client.event
async def on_reaction_add(reaction, user):
    if reaction.me and reaction.count == 1:
        return
    if reaction.message.author == client.user:
        if str(reaction.emoji) == "\u23e9":
           operation = "+"
        elif str(reaction.emoji) == "\u23ea":
            operation = "-"
        else:
            return
        await handleEdit(reaction.message, operation)
    await reaction.remove(user)
    

client.run(TOKEN)