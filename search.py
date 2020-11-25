import csv, discord, os
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
    if prefix in ["%co", "%co+", "%co-", "%co="]:
        url = combio.search(content, n, getCoGenType(prefix))
    elif prefix == "%wiki":
        url = wiki.search(content, n)
    elif prefix == "%yt":
        url = await youtube.search(content, n)
    elif prefix == "%gi":
        n = 0
        embedUrl = gi.search(content, n)
        while gi.checkValidImageUrl(embedUrl) == 0:
            n = n+1
            if n >= 26:
                return "wack"
            embedUrl = gi.search(content, n)
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
    f = open(getDatabase(), 'a')
    f.write(str(createdMessage.id) + "," + str(message.id) + "," + str(content) + "," + str(n) + "," + prefix + "\n")
    f.close()
    await addSelectionArrows(createdMessage)
    return


# Updates a search post to a new result number

async def incrementSearch(row, message, n, prefix):
    if prefix in ["%co", "%co+", "%co-", "%co="]:
        await combio.increment(row, message, n, getDatabase(), getCoGenType(prefix))
    elif prefix == "%wiki":
        await wiki.increment(row, message, n, getDatabase())
    elif prefix == "%yt":
        await youtube.increment(row, message, n, getDatabase())
    elif prefix == "%gi":
        await gi.increment(row, message, n, getDatabase())
    await addSelectionArrows(message)
    return


# parses a general query edit

async def editQuery(message):
    db = getDatabase()
    row = tools.getStoredRowByQueryID(message.id, db)
    updateQuery(message.id, db, tools.getMessageContent(message.content))
    row = tools.getStoredRowByQueryID(message.id, db)
    await incrementSearch(row, await message.channel.fetch_message(row[0]), 0, tools.getMessagePrefix(message.content))


# Parses and executes a general search result increment

async def handleIncrement(reaction, operation, user):
    message = reaction.message
    queryMessage = tools.getStoredRowByID(message.id, getDatabase())
    if queryMessage == -1:
        return -1
    if queryMessage[4] == "%wiki":
        await wiki.increment(queryMessage, message, operation, getDatabase())
    if queryMessage[4] == "%yt":
        await youtube.increment(queryMessage, message, operation, getDatabase())
    if queryMessage[4] == "%gi":
        await gi.increment(queryMessage, message, operation, getDatabase())
    if queryMessage[4] in ["%co", "%co+", "%co-", "%co="]:
        await combio.increment(queryMessage, message, operation, getDatabase(), getCoGenType(queryMessage[4]))
    await reaction.remove(user)
    return


# Adds selection arrows to a message

async def addSelectionArrows(message):
    await message.add_reaction("⏪")
    await message.add_reaction("⏩")

def getCoGenType(prefix):
    genType = 0
    if prefix == "%co+":
        genType = 1
    if prefix == "%co-":
        genType = 2
    if prefix == "%co=":
        genType = 3
    return genType

#return search database
def getDatabase():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmds.csv")
