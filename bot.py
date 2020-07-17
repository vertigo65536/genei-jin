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
import combio_api
from pokedex import pokedex
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


def ytSearch(query, pageToken):
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

async def incrementYt(ytMessage, message, operation):
    if operation == "+":
        pageToken = ytMessage[4]
    elif operation == "-":
        pageToken = ytMessage[3]
    else:
        pageToken = ""
    response = ytSearch(ytMessage[2], pageToken)
    await message.edit(content="https://www.youtube.com/watch?v=" + response['items'][0]['id']['videoId'])
    prevPageToken = ""
    nextPageToken = ""
    if 'prevPageToken' in response.keys():
        prevPageToken = response['prevPageToken']
    if 'nextPageToken' in response.keys():
        nextPageToken = response['nextPageToken']
    updateCounter(message.id, YOUTUBE_DATABASE, [prevPageToken, nextPageToken])
    return
    
def giSearch(message, n):
    response = google_images_download.googleimagesdownload()
    #content = getMessageContent(message.content)
    arguments = {"keywords": message,
                 "limit":n,
                 "offset":n-1,
                 "no_download":True}
    response = response.download(arguments)
    return response[0][message][len(response[0][message]) - 1]
    
async def incrementGi(giMessage, message, operation):
    if operation == "+":
        newCounter = int(giMessage[3])+1
    elif operation == "-":
        newCounter = int(giMessage[3])-1
        if newCounter < 0:
            newCounter = 0
    else:
        newCounter = 0
    newUrl = giSearch(giMessage[2], newCounter)
    e = discord.Embed()
    e.set_image(url=newUrl)
    await message.edit(embed=e)
    updateCounter(message.id, GI_DATABASE, newCounter)
    return

def coSearch(message, n):
    result = combio_api.search(message)[n][1]
    ts = combio_api.getDefaultTimestamps(result)
    return combio_api.getVideoUrl(result, ts)
    
async def incrementCo(coMessage, message, operation):
    if operation == "+":
        newCounter = int(coMessage[3])+1
    elif operation =="-":
        newCounter = int(coMessage[3])-1
        if newCounter < 0:
            newCounter = 0
    else:
        newCounter = 0
    newUrl = coSearch(coMessage[2], newCounter)
    await message.edit(content=newUrl)
    updateCounter(message.id, CO_DATABASE, newCounter)
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
        newCounter = int(wikiMessage[3])+1
    elif operation == "-":
        newCounter = int(wikiMessage[3])-1
        if newCounter < 0:
            newCounter = 0
    else:
        newCounter = 0
    newUrl = wikiSearch(wikiMessage[2], newCounter)
    await message.edit(content=newUrl)
    updateCounter(message.id, WIKI_DATABASE, newCounter)
    return
    
def updateCounter(id, databasePath, newN):
    with open(databasePath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        rows = list(csv_reader)
        for i in range(len(rows)):
            if rows[i-1][0] == str(id):
                if isinstance(newN, list):
                    for j in range(len(newN)):
                        rows[i-1][j+3] = newN[j]
                else:
                    rows[i-1][3] = newN

    with open(databasePath, 'w', newline='\n', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(list(rows))
    return
    
def updateQuery(id, databasePath, newQuery):
    with open(databasePath) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        rows = list(csv_reader)
        for i in range(len(rows)):
            if rows[i-1][1] == str(id):
                rows[i-1][2] = newQuery

    with open(databasePath, 'w', newline='\n', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(list(rows))
    return
    
async def createSearchPost(message):
    prefix = getMessagePrefix(message.content)
    content = getMessageContent(message.content)
    url = ""
    embedUrl = ""
    n = 0
    if prefix == "%co":
        url = coSearch(content, n)
        db = CO_DATABASE
    elif prefix == "%wiki":
        url = wikiSearch(content, n)
        db = WIKI_DATABASE
    elif prefix == "%yt":
        response = ytSearch(content, "")
        url = "https://www.youtube.com/watch?v=" + response['items'][0]['id']['videoId']
        n = ""
        if 'prevPageToken' in response.keys():
            n = n + response['prevPageToken']
        n = n + ","
        if 'nextPageToken' in response.keys():
            n = n + response['nextPageToken']
        db = YOUTUBE_DATABASE
    elif prefix == "%gi":
        n = 0
        embedUrl = giSearch(content, n)
        db = GI_DATABASE
    else:
        return
    if embedUrl == "":
        createdMessage = await message.channel.send(url)
    else:
        e = discord.Embed()
        e.set_image(url=embedUrl)
        createdMessage = await message.channel.send(url, embed=e)
    f = open(db, 'a')
    f.write(str(createdMessage.id) + "," + str(message.id) + "," + str(content) + "," + str(n) + "\n")
    f.close()
    await addSelectionArrows(createdMessage)
    return

async def incrementSearch(row, message, n, prefix):
    print(message.content)
    if prefix == "%co":
        print("test")
        await incrementCo(row, message, n)
    elif prefix == "%wiki":
        await incrementWiki(row, message, n)
    elif prefix == "%yt":
        await incrementYt(row, message, n)
    elif prefix == "%gi":
        await incrementGi(row, message, n)
    else:
        return
    
def selectDatabase(content):
    prefix = getMessagePrefix(content)
    if prefix == "%co":
        db = CO_DATABASE
    elif prefix == "%wiki":
        db = WIKI_DATABASE
    elif prefix == "%yt":
        db = YOUTUBE_DATABASE
    elif prefix == "%gi":
        db = GI_DATABASE
    else:
        return -1
    return db

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

def getStoredRowByID(id, file):
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if row[0] == str(id):
                return row
        return -1
        
def getStoredRowByQueryID(id, file):
    with open(file) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if row[1] == str(id):
                return row
        return -1

async def getPokemon(message):
    content = getMessageContent(message.content)
    dex = pokedex.Pokedex(version='v1', user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    if content.isnumeric():
        pokemon = dex.get_pokemon_by_number(content)[0]
    else:
        pokemon = dex.get_pokemon_by_name(content)[0]
    if len(pokemon['abilities']['hidden']) == 0:
        hidden = "None"
    else:
        hidden = ", ".join(pokemon['abilities']['hidden'])
    e = discord.Embed(title=pokemon['number'] + ": " + pokemon['name'], description=pokemon['description'])
    e.set_thumbnail(url=pokemon['sprite'])
    e.add_field(name="Species", value=pokemon['species'], inline=False)
    e.add_field(name="Types", value=", ".join(pokemon['types']), inline=False)
    e.add_field(name="Abilities", value=", ".join(pokemon['abilities']['normal']), inline=False)
    e.add_field(name="Hidden Abilities", value=hidden, inline=False)
    e.add_field(name="Egg Group(s)", value=", ".join(pokemon['eggGroups']), inline=False)
    e.add_field(name="Gender", value=pokemon['gender'], inline=False)
    e.add_field(name="Height", value=pokemon['height'], inline=False)
    e.add_field(name="Weight", value=pokemon['weight'], inline=False)
    e.add_field(name="Generation", value=pokemon['gen'], inline=False)
    e.add_field(name="Description", value=pokemon['description'], inline=False)
    await message.channel.send(embed=e)
    return

def getLuckyD(content):
    var = requests.get(r'https://duckduckgo.com/?q=!' + urllib.parse.quote(content) + "%3Asiteurl", allow_redirects=True)
    return var.url
    
def getLuckyG(content):
    var = requests.get(r'https://www.google.com/search?btnI=1&q=' + urllib.parse.quote(content), headers = {"Referer": "http://www.google.com/"}, allow_redirects=True)
    return var.url.replace("https://www.google.com/url?q=", "")

async def sunnySub(message):
    soundFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'sunny.mp3')
    fontName = 'Textile'
    outputFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'sunny.mp4')
    subtitle = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'sunny.srt').replace("C:", "").replace("\\", "/")
    content = message.content.title()
    
    f = open(subtitle, "w")
    f.write("1\n00:00:00,000 --> 00:00:07,000\n" + content)
    f.close()
    
    ffmpegCmd = "ffmpeg -y -f lavfi -i color=size=320x240:duration=5:rate=25:color=black -i \"" + soundFile + "\" -vf \"subtitles=" + subtitle + ":force_style=\'fontsize=30,fontcolor=white,Alignment=10,FontName=" + fontName + "'\" \"" + outputFile + '"'
    os.system(ffmpegCmd)
    file = discord.File(outputFile, filename=content + ".mp4")
    await message.channel.send(file=file)
    if os.path.exists(outputFile):
        os.remove(outputFile)
    if os.path.exists(subtitle):
        os.remove(subtitle)
    return

async def handleMessage(message):
    prefix = getMessagePrefix(message.content)
    content = getMessageContent(message.content)
    if prefix == "%ping":
        return "pong"
    elif prefix in ["%co", "%wiki", "%yt", "%gi"]:
        return await createSearchPost(message)
    elif isLoneEmoji(message):
        return await bigmoji(message)
    elif prefix == "%title":
        return await setTitle(message)
    elif prefix == "%ctitle":
        return await setChannelTitle(message)
    elif prefix == "%topic":
        return await setTopic(message)
    elif prefix == "%man" or prefix == "%help":
        return getManPage()
    elif prefix == "%dex":
        return await getPokemon(message)
    elif prefix == "%lucky":
        return getLuckyG(content)
    elif message.content.lower().startswith("the gang "):
        return await sunnySub(message)
    return
    

async def handleEdit(reaction, operation, user):
    message = reaction.message
    wikiMessage = getStoredRowByID(message.id, WIKI_DATABASE)
    ytMessage = getStoredRowByID(message.id, YOUTUBE_DATABASE)
    giMessage = getStoredRowByID(message.id, GI_DATABASE)
    coMessage = getStoredRowByID(message.id, CO_DATABASE)
    if wikiMessage != -1:
        await incrementWiki(wikiMessage, message, operation)
    if ytMessage != -1:
        await incrementYt(ytMessage, message, operation)
    if giMessage != -1:
        await incrementGi(giMessage, message, operation)
    if coMessage != -1:
        await incrementCo(coMessage, message, operation)
    await reaction.remove(user)
    return

async def editQuery(message):
    db = selectDatabase(message.content)
    row = getStoredRowByQueryID(message.id, db)
    updateQuery(message.id, db, getMessageContent(message.content))
    row = getStoredRowByQueryID(message.id, db)
    await incrementSearch(row, await message.channel.fetch_message(row[0]), 0, getMessagePrefix(message.content))
    

def initDatabases():
    open(YOUTUBE_DATABASE, 'w').close()
    open(WIKI_DATABASE, 'w').close()
    open(GI_DATABASE, 'w').close()
    open(CO_DATABASE, 'w').close()
    return
    

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

YOUTUBE_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube.csv")
WIKI_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki.csv")
GI_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gi.csv")
CO_DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "co.csv")

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
        await handleEdit(reaction, operation, user)

@client.event
async def on_message_edit(before, after):
    if after.author == client.user:
        return
    else:
        await editQuery(after)
    return

client.run(TOKEN)