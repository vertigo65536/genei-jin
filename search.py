import csv, discord
import tools, youtube, combio, wiki, gi


# Updates the database entry of result message with a new query value

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


# parses and executes a search result query. Posts the result to discord

async def createSearchPost(message):
    prefix = tools.getMessagePrefix(message.content)
    content = tools.getMessageContent(message.content)
    url = ""
    embedUrl = ""
    n = 0
    if prefix == "%co":
        url = combio.search(content, n)
        db = combio.getDatabase()
    elif prefix == "%wiki":
        url = wiki.search(content, n)
        db = wiki.getDatabase()
    elif prefix == "%yt":
        url = await youtube.search(content, n)
        db = youtube.getDatabase()
    elif prefix == "%gi":
        n = 0
        embedUrl = gi.search(content, n)
        while gi.checkValidImageUrl(embedUrl) == 0:
            n = n+1
            if n >= 26:
                return "wack"
            embedUrl = gi.search(content, n)
        db = gi.getDatabase()
    else:
        return
    if url == -1 or embedUrl == -1:
        return "no results you fucking cuck"
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


# Updates a search post to a new result number

async def incrementSearch(row, message, n, prefix):
    if prefix == "%co":
        await combio.increment(row, message, n)
    elif prefix == "%wiki":
        await wiki.increment(row, message, n)
    elif prefix == "%yt":
        await youtube.increment(row, message, n)
    elif prefix == "%gi":
        await gi.increment(row, message, n)
    await addSelectionArrows(message)
    return


# parses a general query edit

async def editQuery(message):
    db = selectDatabase(message.content)
    row = tools.getStoredRowByQueryID(message.id, db)
    updateQuery(message.id, db, tools.getMessageContent(message.content))
    row = tools.getStoredRowByQueryID(message.id, db)
    await incrementSearch(row, await message.channel.fetch_message(row[0]), 0, tools.getMessagePrefix(message.content))


# Parses and executes a general search result increment

async def handleIncrement(reaction, operation, user):
    message = reaction.message
    wikiMessage = tools.getStoredRowByID(message.id, wiki.getDatabase())
    ytMessage = tools.getStoredRowByID(message.id, youtube.getDatabase())
    giMessage = tools.getStoredRowByID(message.id, gi.getDatabase())
    coMessage = tools.getStoredRowByID(message.id, combio.getDatabase())
    if wikiMessage != -1:
        await wiki.increment(wikiMessage, message, operation)
    if ytMessage != -1:
        await youtube.increment(ytMessage, message, operation)
    if giMessage != -1:
        await gi.increment(giMessage, message, operation)
    if coMessage != -1:
        await combio.increment(coMessage, message, operation)
    await reaction.remove(user)
    return


# Adds selection arrows to a message

async def addSelectionArrows(message):
    await message.add_reaction("⏪")
    await message.add_reaction("⏩")


# Takes message string and returns the correct database for the comimand
# used, returns -1 if no valid database

def selectDatabase(content):
    prefix = tools.getMessagePrefix(content)
    if prefix == "%co":
        db = combio.getDatabase()
    elif prefix == "%wiki":
        db = wiki.getDatabase()
    elif prefix == "%yt":
        db = youtube.getDatabase()
    elif prefix == "%gi":
        db = gi.getDatabase()
    else:
        return -1
    return db
