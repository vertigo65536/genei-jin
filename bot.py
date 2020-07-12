import os
import requests
import discord
import json
import urllib.parse
from google_images_download import google_images_download
import you
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
    href = 'https://www.youtube.com/results?search_query=' + urllib.parse.quote(message)
    page = requests.get(href)
    soup = BeautifulSoup(page.text, features='html.parser')
    videos = []
    for video in soup.findAll('a'):
        print(video)
        if 'id' in video and video['id'] == 'video-title':
            videos.append(video['value'])
    print(videos)
    return "test"
    
def giSearch(message):
    #gis = GoogleImagesSearch(os.getenv('GOOGLE_IMAGES_API_KEY'), os.getenv('GCS_CX'))

    #define search params:
    #_search_params = {
    #    'q': message,
    #    'num': 1,
    #    'safe': 'off'
    #}
    #result = gis.search(search_params=_search_params)
    
    #print(result)
    
    response = google_images_download.googleimagesdownload()
    
    arguments = {"keywords": message,
                 "limit":4, 
                 "print_urls":True}  
    print(response.download(arguments))
    return -1
        
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

def handleMessage(message):
    prefix = getMessagePrefix(message)
    content = getMessageContent(message)
    if prefix == "%co":
        return combQuote(content)
    #elif prefix == "%yt":
    #    return ytSearch(content)
    #elif prefix == "%gi":
    #    return giSearch(content)
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
    response = handleMessage(message.content)
    if response != None:
        await message.channel.send(response)
    else:
        return
client.run(TOKEN)