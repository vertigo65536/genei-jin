import csv, discord, os
import tools, youtube, combio, wiki, gi, game, yugioh, dictionary, lego, gifglobe, scenesearch

# Updates the database entry of result message with a new query value

def updateQuery(id, db, newQuery, prefix):
    with open(db) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        rows = list(csv_reader)
        for i in range(len(rows)):
            if rows[i-1][1] == str(id):
                rows[i-1][2] = newQuery
                rows[i-1][4] = prefix

    with open(db, 'w', newline='\n', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(list(rows))
    return


# parses and executes a search result query. Posts the result to discord

async def createSearchPost(message, outputPrefix=""):
    async with message.channel.typing():
        prefix = tools.getMessagePrefix(message.content)
        modifier = None
        if prefix[-1] in ["+", "-", "=", "."]:
            modifier = prefix[-1]
            prefix = prefix[:-1]
        content = tools.getMessageContent(message.content)
        url = ""
        n = 0
        error = 0
        searchType = getSearchType(prefix)
        e = None
        results = await searchType.search(content, n, prefix, modifier)
        print(searchType)
        try:
            results = await searchType.search(content, n, prefix, modifier)
        except:
            url = "No answer from server"
            error = 1
        else:
            e = await searchType.getEmbed(results, tools.getUserColour(message.author))
            if e == None:
                url = results
        if error != 1 and results == -1:
            url = "no results you fucking cuck"
            error = 1
    linesplit = url.split('\n')
    for i in range(len(linesplit)):
        linesplit[i] = outputPrefix + linesplit[i]
    url = '\n'.join(linesplit)
    createdMessage = await message.channel.send(url, embed=e)
    f = open(getDatabase(), 'a')
    if modifier == None:
        modifier = ""
    f.write(str(createdMessage.id) + "," + str(message.id) + "," + str(content) + "," + str(n) + "," + prefix + modifier + "\n")
    f.close()
    if error == 0 and prefix not in ["%def"]:
        await addSelectionArrows(createdMessage)
    return


# Updates a search post to a new result number

async def incrementSearch(row, message, n, prefix):
    await increment(row, message, n, getDatabase())
    await addSelectionArrows(message)
    return


# parses a general query edit

async def editQuery(message):
    db = getDatabase()
    content = tools.getMessageContent(message.content)
    prefix = tools.getMessagePrefix(message.content)
    row = tools.getStoredRowByQueryID(message.id, db)
    updateQuery(message.id, db, content, prefix)
    row = tools.getStoredRowByQueryID(message.id, db)
    await incrementSearch(row, await message.channel.fetch_message(row[0]), 0, prefix)


# Parses and executes a general search result increment

async def handleIncrement(reaction, operation, user):
    message = reaction.message
    queryMessage = tools.getStoredRowByID(message.id, getDatabase())
    if queryMessage == -1:
        return -1
    await increment(queryMessage, message, operation, getDatabase(), user)
    await reaction.remove(user)
    return


# Adds selection arrows to a message

async def addSelectionArrows(message):
    await message.add_reaction("⏪")
    await message.add_reaction("⏩")

def getSearchType(prefix):
    if prefix == "%ss":
        return scenesearch
    if prefix == "%yt":
        return youtube
    if prefix == "%wiki":
        return wiki
    if prefix == "%gi":
        return gi
    if prefix == "%co":
        print("poopy")
        return combio
    if prefix == "%game":
        return game
    if prefix == "%yu":
        return yugioh
    if prefix == "%def":
        return dictionary
    if prefix == "%lego":
        return lego
    if prefix in [
                "%ft",
                "%fatherted",
                "%mb",
                "%mightyboosh",
                "%dt",
                "%daytoday",
                "%bb",
                "%blackbooks",
                "%alanpartridge",
                "%ps",
                "%peepshow",
                "%office",
                "%toi",
                "%thickofit",
                "%log",
                "%leagueofgentlemen"
            ]:
        return gifglobe
    if prefix in [
            "%sunny",
            "%avgn",
            "%pp",
            "%sp",
            "%sb",
            "%bd",
            "%ap",
            "%sg",
            "%koth"
        ]:
        return scenesearch


async def increment(queryMessage, message, operation, db, user=None):
    if operation == "+":
        newCounter = int(queryMessage[3])+1
    elif operation =="-":
        newCounter = int(queryMessage[3])-1
    else:
        newCounter = 0
    prefix = queryMessage[4]
    modifier = None
    if prefix[-1] in ["+", "-", "=", "."]:
        modifier = prefix[-1]
        prefix = prefix[:-1]
    search = getSearchType(prefix)
    results = await search.search(queryMessage[2], newCounter, prefix, modifier=modifier)
    if results == -1:
        return
    elif results == -2:
        newCounter = 0
        results = await search.search(queryMessage[2], newCounter, prefix, modifier=modifier)
    if 'n_value' in results:
        newCounter = results['n_value']
    elif isinstance(results, int):
        newCounter = results
        results = await search.search(queryMessage[2], newCounter, prefix, modifier=modifier)
    newUrl = None
    if user == None:
        colour = tools.getUserColour(message.author)
    else:
        colour = tools.getUserColour(user)
    e = await search.getEmbed(results, colour)
    if e == None:
        newUrl = results
    await message.edit(content=newUrl, embed = e)
    tools.updateCounter(message.id, db, newCounter)
    return

#return search database
def getDatabase():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmds.csv")
