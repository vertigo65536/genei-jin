import os
import re
import requests
import discord
import json
import random
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import you
import csv
import urllib.request as urllib2
import time
import urllib
import search, tools, stats
from pokedex import pokedex
#from google_images_download import google_images_download
from bs4 import BeautifulSoup
from dotenv import load_dotenv

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
    newTitle = name=tools.getMessageContent(message.content)
    await message.guild.edit(name=newTitle)
    return
    
async def setChannelTitle(message):
    newTitle = tools.getMessageContent(message.content)
    await message.channel.edit(name=str(newTitle))
    return
    
async def setTopic(message):
    newTopic = tools.getMessageContent(message.content)
    await message.channel.edit(topic=str(newTopic))
    return
    
def getManPage():
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "man.txt"), "r")
    if f.mode == "r":
        return f.read()
    print("Failed to open man file")
    return


def getNewestRow():
    databases = [YOUTUBE_DATABASE, CO_DATABASE, WIKI_DATABASE, GI_DATABASE]
    eachNewestRow = [[],[],[],[]]
    for i in range(len(databases)):
        with open(databases[i]) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            data = []
            for row in csv_reader:
                data.append(row)
            if len(data) > 0:
                eachNewestRow[i] = data[-1]
    counter = -1
    for i in range(len(eachNewestRow)):
        if eachNewestRow[i] == []:
            continue
        if eachNewestRow[counter] == []:
            counter = i
            continue
        if eachNewestRow[i][0] > eachNewestRow[counter][0]:
            counter = i
    return eachNewestRow[counter]

def newestRow(operation):
    databases = {
    "yt": YOUTUBE_DATABASE,
    "co": CO_DATABASE,
    "wiki": WIKI_DATABASE,
    "gi":  GI_DATABASE
    }
    eachNewestRow = {}
    for database in databases:
        with open(databases[database]) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            data = []
            for row in csv_reader:
                data.append(row)
            if len(data) > 0:
                eachNewestRow[database] = data[-1]
            else:
                eachNewestRow[database] = -1
    counter = -1
    for row in eachNewestRow:
        if eachNewestRow[row] == -1:
            continue
        if counter == -1:
            counter = row
            continue
        if eachNewestRow[row][0] > eachNewestRow[counter][0]:
            counter = row
    if operation == "get":
        return eachNewestRow[counter]
    if operation == "type":
        return counter
    if operation == "del":
        with open(databases[counter]) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            data = []
            for row in csv_reader:
                data.append(row)
            del data[-1]
        with open(databases[counter], "w+") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(data)
    return

async def getPokemon(message):
    content = tools.getMessageContent(message.content)
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

async def getRedditLink(messageData):
    content = messageData.content.split(" ")
    message = ""
    for i in range(len(content)):
        if content[i].startswith("/r/"):
           url = "https://old.reddit.com" + content[i]
           if requests.get(url, allow_redirects=True).url == url:
               message = message + url + "\n" 
    if message != "":
        await messageData.channel.send(message)

async def deleteLastCommand(message):
    row = newestRow('get')
    botMessage = await message.channel.fetch_message(row[0])
    userMessage = await message.channel.fetch_message(row[1])
    await message.channel.delete_messages([botMessage, userMessage, message])
    newestRow('del')
    return

def getStats(user, content):
    userId = str(user.id)
    rawStats = stats.getFileAsArray(stats.checkAndCreateStats(userId))
    readableTime = time.ctime(float(str.rstrip(rawStats[0])))
    if content == -1:
        formattedStats = "Commands used since " + readableTime + " by " + user.name + "\n"
        for i in range(1, len(rawStats)):
            formattedStats = formattedStats+rawStats[i]
        return formattedStats
    else:
        content = str.lower(content)
        value = stats.getStatValue(userId, content)
        if value == None:
            value = stats.getStatValue(userId, "%" + content)
        if value == None:
            value = "No stat found for " + content
        else:
            value = content + " used " + str(value) + " times since " + readableTime + " by " + user.name
        return value

async def trophyPost(trophyId, message, user):
    user = str(await client.fetch_user(user))[:-5]
    trophyData = stats.getTrophyList()[trophyId]
    e = discord.Embed(title=user + " has earned the trophy: ***" + trophyData['name'] + "***", description=trophyData['description'])
    e.set_thumbnail(url=stats.getTrophyIcon(trophyData['tier']))
    await message.channel.send(embed=e)

def getUserId(user):
    userPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(userPath) as json_file:
        data = json.load(json_file)
        try:
            return data[user]
        except:
            return -1

 
async def trophyProcess(trophyId, message):
    if message.author.bot == True:
        return
    trophyInfo = stats.getTrophyList()[trophyId]
    trophyCheck = stats.getTrophyValue(message.author.id, trophyId)
    n = stats.getStatValue(message.author.id, str(trophyInfo['stat']))
    if trophyCheck == "False" and n >= trophyInfo['criteria']:
        stats.editTrophy(message.author.id, trophyId)
        await trophyPost(trophyId, message, message.author.id)
    if stats.checkPlat(message.author.id) == 1:
        await awardTrophy("plat", message.author.id, message)

async def awardTrophy(trophyId, user, message):
    if user == -1:
        return "Invalid User"
    stats.editTrophy(user, trophyId)
    await trophyPost(trophyId, message, user)
    if stats.checkPlat(user) == 1:
        await awardTrophy("plat", user, message)


async def handleMessage(message):
    prefix = tools.getMessagePrefix(message.content)
    content = tools.getMessageContent(message.content)
    output = ""
    trophy = -1
    stat = -1
    cmd = 0
    recieveId = message.author.id
    if prefix == "%ping":
        cmd = 1
        stat = prefix
        output = "pong"
    elif prefix in ["%co", "%wiki", "%yt", "%gi"]:
        cmd = 1
        trophy = prefix
        stat = prefix
        output = await search.createSearchPost(message)
    elif isLoneEmoji(message):
        cmd = 1
        trophy = "bigmoji"
        stat = "bigmoji"
        output = await bigmoji(message)
    elif prefix == "%title":
        cmd = 1
        stat = prefix
        output = await setTitle(message)
    elif prefix == "%ctitle":
        cmd = 1
        stat = prefix
        output = await setChannelTitle(message)
    elif prefix == "%topic":
        cmd = 1
        stat = prefix
        output = await setTopic(message)
    elif prefix == "%man" or prefix == "%help":
        cmd = 1
        stat = "%man"
        output = getManPage()
    elif prefix == "%dex":
        cmd = 1
        stat = prefix
        output = await getPokemon(message)
    elif prefix == "%lucky":
        cmd = 1
        stat = prefix
        output = getLuckyG(content)
    elif message.content.lower().startswith("the gang "):
        cmd = 1
        stat = "sunny"
        output = await sunnySub(message)
    elif prefix == "%canyoufitabillionmothsin32hamptonroad'slivingroom":
        trophy = "hampton"
        cmd = 1
        stat = prefix
        output = "Yes"
    elif "69" in message.content.split(" "):
       trophy = "nice"
       stat = "69"
       await message.add_reaction("🇳")
       await message.add_reaction("🇮")
       await message.add_reaction("🇨")
       await message.add_reaction("🇪")
    elif message.content == "`":
        cmd = 1
        stat = "delete"
        output = await deleteLastCommand(message)
    elif prefix == "%stats":
        cmd = 1
        stat = prefix
    elif any(word in str.lower(message.content) for word in ['shid', 'shidding', 'shidded', 'fard', 'farding', 'farded']):
        stat = "shidandfard"
        trophy = "shid"
    elif prefix == "%bugreport":
        if str(message.author.id) != os.getenv('ADMIN_ID'):
            output = "not admin"
        else:
            recieveId = getUserId(content)
            output = await awardTrophy("bug", recieveId, message) 
    elif prefix == "%featurerequest":
        if str(message.author.id) != os.getenv('ADMIN_ID'):
            output = "not admin"
        else:
            recieveId = getUserId(content)
            output = await awardTrophy("feature", recieveId, message)
    elif prefix == "%trophylist" or prefix == "%tl":
        output = stats.getReadableTrophyList()
    elif prefix == "%mytrophys" or prefix == "%mt":
        trophys = stats.getTrophyList()
        for key in trophys:
            if stats.getTrophyValue(message.author.id, key) == "True":
                await trophyPost(key, message, message.author.id)
    elif prefix == "%trophystat" or prefix == "%ts":
        trophys = stats.getTrophyList()
        trophyArray = []
        for key in trophys:
            trophyArray.append([trophys[key]['name'], int(stats.getTrophyStat(key))])
        trophyArray = sorted(trophyArray, key=lambda x: x[1], reverse=True)
        string = ""
        for i in range(len(trophyArray)):
            string = string + trophyArray[i][0] + ": " + str(trophyArray[i][1]) + "%\n"
        return string
    if stat != -1:
        stats.checkAndCreateStats(message.author.id)
        stats.checkAndCreateTrophy(message.author.id)
        stats.writeStat(str(message.author.id), stat)
    if cmd == 1:
        stats.writeStat(str(message.author.id), "all")
        await trophyProcess("first", message)
        await trophyProcess("cmds", message)
    if message.content[0] == "/":
        await trophyProcess("cylon", message)
    if trophy != -1:
        await trophyProcess(trophy, message)
    if prefix == "%stats":
        output = getStats(message.author, content)
    await getRedditLink(message)
    if stats.checkPlat(recieveId) == 1:
        await awardTrophy("plat", recieveId, message)
    return output
    

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
    if response != "" and response != None:
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
        await search.handleIncrement(reaction, operation, user)

@client.event
async def on_message_edit(before, after):
    if after.author == client.user:
        return
    else:
        await search.editQuery(after)
    return

@client.event
async def on_message_delete(message):
    await trophyProcess("delete", message)

client.run(TOKEN)
