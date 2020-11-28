import csv, discord, os
import tools, youtube, combio, wiki, gi, game


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

async def createSearchPost(message):
    prefix = tools.getMessagePrefix(message.content)
    content = tools.getMessageContent(message.content)
    url = ""
    embedUrl = ""
    n = 0
    error = 0
    searchType = getSearchType(prefix)
    try:
        results = await searchType.search(content, n, prefix)
    except:
        url = "No answer from server"
        error = 1
    else:
        e = await searchType.getEmbed(results)
        if e == None:
            url = results
    if url == -1 or embedUrl == -1:
        url = "no results you fucking cuck"
        error = 1
    createdMessage = await message.channel.send(url, embed=e)
    f = open(getDatabase(), 'a')
    f.write(str(createdMessage.id) + "," + str(message.id) + "," + str(content) + "," + str(n) + "," + prefix + "\n")
    f.close()
    if error == 0:
        await addSelectionArrows(createdMessage)
    return


# Updates a search post to a new result number

async def incrementSearch(row, message, n, prefix):
    await getSearchType(prefix).increment(row, message, n, getDatabase())
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
    await getSearchType(queryMessage[4]).increment(queryMessage, message, operation, getDatabase())
    await reaction.remove(user)
    return


# Adds selection arrows to a message

async def addSelectionArrows(message):
    await message.add_reaction("⏪")
    await message.add_reaction("⏩")

def getSearchType(prefix):
    if prefix == "%yt":
        return youtube
    if prefix == "%wiki":
        return wiki
    if prefix == "%gi":
        return gi
    if "%co" in prefix:
        return combio
    if prefix == "%game":
        return game

#return search database
def getDatabase():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmds.csv")
