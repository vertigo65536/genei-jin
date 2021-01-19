import csv, discord, os
import tools, youtube, combio, wiki, gi, game, yugioh, dictionary, lego


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
    async with message.channel.typing():
        prefix = tools.getMessagePrefix(message.content)
        content = tools.getMessageContent(message.content)
        url = ""
        n = 0
        error = 0
        searchType = getSearchType(prefix)
        e = None
        try:
            results = await searchType.search(content, n, prefix)
        except:
            url = "No answer from server"
            error = 1
        else:
            e = await searchType.getEmbed(results)
            if e == None:
                url = results
        if error != 1 and results == -1:
            url = "no results you fucking cuck"
            error = 1
    createdMessage = await message.channel.send(url, embed=e)
    f = open(getDatabase(), 'a')
    f.write(str(createdMessage.id) + "," + str(message.id) + "," + str(content) + "," + str(n) + "," + prefix + "\n")
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
    await increment(queryMessage, message, operation, getDatabase())
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
    if prefix == "%yu":
        return yugioh
    if prefix == "%def":
        return dictionary
    if prefix == "%lego":
        return lego


async def increment(queryMessage, message, operation, db):
    if operation == "+":
        newCounter = int(queryMessage[3])+1
    elif operation =="-":
        newCounter = int(queryMessage[3])-1
    else:
        newCounter = 0
    search = getSearchType(queryMessage[4])
    results = await search.search(queryMessage[2], newCounter, queryMessage[4])
    if results == -1:
        return
    elif results == -2:
        newCounter = 0
        results = await search.search(queryMessage[2], newCounter, queryMessage[4])
    if 'n_value' in results:
        newCounter = results['n_value']
    elif isinstance(results, int):
        newCounter = results
        results = await search.search(queryMessage[2], newCounter, queryMessage[4])
    newUrl = None
    e = await search.getEmbed(results)
    if e == None:
        newUrl = results
    await message.edit(content=newUrl, embed = e)
    tools.updateCounter(message.id, db, newCounter)
    return

#return search database
def getDatabase():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "cmds.csv")
