import os, re, requests, discord, json, time, urllib, csv, subprocess, aiohttp, openai
import search, tools, stats
from pokedex import pokedex
from bs4 import BeautifulSoup
from dotenv import load_dotenv

#Gets a response from chatGPT from a prompt

def chatgpt(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0, max_tokens=380)
    return response['choices'][0]['text']

# Checks if a message only contains a single emoji, and no attachment

def isLoneEmoji(message):
    pattern = re.compile('<:\w*:\d*>$')
    if pattern.match(message.content) and not message.attachments:
        return 1
    else:
        return 0


# Posts a larger version of an emoji, and deletes the original message.
# Sets colour as original user's colour

async def randomJoke():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://official-joke-api.appspot.com/random_joke') as r:
            if r.status != 200:
                raise RuntimeError(f'{r.status} - {r.reason}')
            returnJson = (await r.json())
            outputString = returnJson['setup'] + "\n\n||" + returnJson['punchline'] + "||"
            return outputString
            
 

async def bigmoji(message):
    id = message.content[1:-1].split(':')[2]
    imageUrl = "https://cdn.discordapp.com/emojis/" + id
    e = discord.Embed(colour=tools.getUserColour(message.author))
    e.set_image(url=imageUrl)
    await message.channel.send("", embed=e)
    await message.delete()
    return


# Set guild title

async def setTitle(message):
    newTitle = name=tools.getMessageContent(message.content)
    await message.guild.edit(name=newTitle)
    return
    

# Set channel title

async def setChannelTitle(message):
    newTitle = tools.getMessageContent(message.content)
    await message.channel.edit(name=str(newTitle))
    return
    

# Set channel topic

async def setTopic(message):
    newTopic = tools.getMessageContent(message.content)
    await message.channel.edit(topic=str(newTopic))
    return
    

# Returns man page as string

def getManPage():
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "man.txt"), "r")
    if f.mode == "r":
        return f.read()
    print("Failed to open man file")
    return


#Returns the newest row in the search query DB
def getNewestRow():
    line = subprocess.check_output(['tail', '-1', search.getDatabase()])[0:-1].decode()
    return line.split(',')

#deletes the newest row in the search query db

def delNewestRow():
    with open(search.getDatabase()) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        data = []
        for row in csv_reader:
            data.append(row)
        del data[-1]
    with open(search.getDatabase(), "w+") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(data)



# Searches pokedex for pokemon and returns pokedex entry

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
    await message.channel.send(embed=e)
    return

#Get text from image

def ocr_space_url(url, overlay, api_key, language='eng'):
    """ OCR.space API request with remote file.
        Python3.5 - not tested on 2.7
    :param url: Image url.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'url': url,
               'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    r = requests.post('https://api.ocr.space/parse/image',
                      data=payload,
                      )
    return json.loads(r.content.decode())

# Returns imfeelinglucky search result for DuckDuckGo

def getLuckyD(content):
    var = requests.get(r'https://duckduckgo.com/?q=!' + urllib.parse.quote(content) + "%3Asiteurl", allow_redirects=True)
    return var.url
    

# Returns imfeelinglucky search result for Google

def getLuckyG(content):
    var = requests.get(r'https://www.google.com/search?btnI=1&q=' + urllib.parse.quote(content), headers = {"Referer": "http://www.google.com/", "Cookie": "CONSENT=YES+GB.en+20151207-13-0"}, allow_redirects=True)
    return var.url.replace("https://www.google.com/url?q=", "")


# Converts a string to an "It's Always Sunny in Philadelphia" style title
# sequence

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


# Returns an array of links to all subreddits in a string

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


# Deletes last bot command in channel given message was sent in

async def deleteLastCommand(message):
    row = getNewestRow()
    botMessage = await message.channel.fetch_message(row[0])
    userMessage = await message.channel.fetch_message(row[1])
    await message.channel.delete_messages([botMessage, userMessage, message])
    delNewestRow()
    return

# returns formatted user bot usage stats. content is empty returns all, else returns stats of given command

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


# Posts a trophy

async def trophyPost(trophyId, message, user):
    user = str(await client.fetch_user(user))[:-5]
    trophyData = stats.getTrophyList()[trophyId]
    e = discord.Embed(title=user + " has earned the trophy: ***" + trophyData['name'] + "***", description=trophyData['description'])
    e.set_thumbnail(url=stats.getTrophyIcon(trophyData['tier']))
    await message.channel.send(embed=e)


# Check if a user has earned a trophy, and if so, awards it
 
async def trophyProcess(trophyId, message):
    print(message.guild.id)
    if message.guild.id not in [731319735404462253, 370919425517551616]:
        return
    if message.author.bot == True:
        return
    if "%co" in trophyId:
        trophyId = "%co"
    trophyInfo = stats.getTrophyList()[trophyId]
    trophyCheck = stats.getTrophyValue(message.author.id, trophyId)
    n = stats.getStatValue(message.author.id, str(trophyInfo['stat']))
    if trophyCheck == "False" and n >= trophyInfo['criteria']:
        stats.editTrophy(message.author.id, trophyId)
        await trophyPost(trophyId, message, message.author.id)
    if stats.checkPlat(message.author.id) == 1:
        await awardTrophy("plat", message.author.id, message)


# Manually awards a user a trophy

async def awardTrophy(trophyId, user, message):
    if user == -1:
        return "Invalid User"
    stats.editTrophy(user, trophyId)
    await trophyPost(trophyId, message, user)
    if stats.checkPlat(user) == 1:
        await awardTrophy("plat", user, message)


async def changeNickname(message):
    messageSplit = message.content.split(' ')
    userId = tools.getUserId(messageSplit[1].lower())
    del messageSplit[0]
    del messageSplit[0]
    await message.guild.get_member(int(userId)).edit(nick=" ".join(messageSplit))
    return

# Takes a recieved message and checks if it is a bot function.
# Executes it if so

async def handleMessage(message):
    stat = -1
    trophy = -1
    output = ""
    cmd = 0
    if len(message.attachments) > 0 :
        for attachment in message.attachments:
            imageText = ocr_space_url(attachment.url, False, OCR)
            if "69" in imageText['ParsedResults'][0]['ParsedText']:
                await message.add_reaction("🇳")
                await message.add_reaction("🇮")
                await message.add_reaction("🇨")
                await message.add_reaction("🇪") 
    if len(message.content) > 0:
        hashes = len(message.content) - len(message.content.lstrip('#'))
        outputPrefix = ""
        for i in range(hashes):
            outputPrefix = outputPrefix + "#"
        if hashes > 0:
            outputPrefix = outputPrefix + " "
        message.content = message.content.lstrip('#').lstrip(' ')
        message.content = message.content.strip('|')
        prefix = tools.getMessagePrefix(message.content)
        content = tools.getMessageContent(message.content)
        recieveId = message.author.id
        if prefix == "%ping":
            cmd = 1
            stat = prefix
            output = "pong"
        elif prefix == "%chat":
            output = chatgpt(content)
        elif message.content.lower() == "fuck you":
            output = 'Don\'t know how to "FUCK" something.'
        elif message.content.lower() == "eat pillow":
            output = "Yuck!"
        elif prefix in [
                    "%co",
                    "%co+",
                    "%co-",
                    "%co=",
                    "%wiki",
                    "%yt",
                    "%gi",
                    "%game",
                    "%yu",
                    "%def",
                    "%lego",
                    "%ft",
                    "%fatherted",
                    "%mb",
                    "%mightyboosh",
                    "%dt",
                    "%daytoday",
                    "%bb",
                    "%blackbooks",
                    "%ap",
                    "%alanpartridge",
                    "%ps",
                    "%peepshow",
                    "%office",
                    "%toi",
                    "%thickofit",
                    "%log",
                    "%leagueofgentlemen"
                ]:
            cmd = 1
            if prefix not in  [
                            "%game",
                            "%yu",
                            "%def",
                            "%lego",
                            "%ft",
                            "%ft",
                            "%fatherted",
                            "%mb",
                            "%mightyboosh",
                            "%dt",
                            "%daytoday",
                            "%bb",
                            "%blackbooks",
                            "%ap",
                            "%alanpartridge",
                            "%ps",
                            "%peepshow",
                            "%office",
                            "%toi",
                            "%thickofit",
                            "%log",
                            "%leagueofgentlemen"
                        ]:
                trophy = prefix
            stat = prefix
            output = await search.createSearchPost(message, outputPrefix)
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
        elif prefix == "%nick":
            cmd = 1
            stat = prefix
            output = await changeNickname(message)
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
        elif prefix == "%joke":
            cmd = 1
            stat = prefix
            output = await randomJoke()
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
        elif prefix.lower() in ["/gdq", "/schedule"]:
            output = "https://pbs.twimg.com/media/D9yQ4dlXUAACQtH.jpg"
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
                recieveId = tools.getUserId(content)
                output = await awardTrophy("bug", recieveId, message) 
        elif prefix == "%featurerequest":
            if str(message.author.id) != os.getenv('ADMIN_ID'):
                output = "not admin"
            else:
                recieveId = tools.getUserId(content)
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
    

# Initialises databases

def initDatabases():
    open(search.getDatabase(), 'w').close()
    return
    

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OCR = os.getenv('OCR_SPACE')
#intents = discord.Intents.default()
intents = discord.Intents.all()
intents.members = True
client = discord.Client(intents=intents)
initDatabases()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name="shid and fard all over the place"))
    
@client.event    
async def on_message(message):
    if message.author == client.user:
        return
    response = await handleMessage(message)
    if response != "" and response != None:
        await message.channel.send(prefix + response)
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
