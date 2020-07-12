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
from google_images_download import google_images_download
from bs4 import BeautifulSoup
from dotenv import load_dotenv


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
    
def ytSearch(message):
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "YOUR_CLIENT_SECRET_FILE.json"
    
    
    developerKey = os.getenv("YOUTUBE_API_KEY")
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=developerKey)

    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=message
    )
    response = request.execute()

    id = response['items'][0]['id']['videoId']
    return "https://www.youtube.com/watch?v=" + id
    
async def giSearch(message):
    response = google_images_download.googleimagesdownload()
    content = getMessageContent(message.content)
    arguments = {"keywords": content,
                 "limit":1, 
                 "print_urls":True}
    await message.channel.send(file=discord.File(str(response.download(arguments)[0][content][0])))
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

def getWikiPage(searchResult):
    try:
        page = wikipedia.page(searchResult)
        return(page)
    except wikipedia.DisambiguationError as e:
        return getWikiPage(random.choice(e.options))

def wikiSearch(message):
    search = wikipedia.search(message)
    return getWikiPage(search[0]).url
    
async def handleMessage(message):
    prefix = getMessagePrefix(message.content)
    content = getMessageContent(message.content)
    if prefix == "%co":
        return combQuote(content)
    elif isLoneEmoji(message):
        return await bigmoji(message)
    elif prefix == "%wiki":
        return wikiSearch(content)
    elif prefix == "%yt":
        return ytSearch(content)
    elif prefix == "%gi":
        return await giSearch(message)
        
    #test functions
    if str(message.guild.id) == "731319735404462253": 
        print("test function - may not run correctly")
    return


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

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
client.run(TOKEN)