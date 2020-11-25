import csv, os, json

# Returns the first word from a string (Usually a bot command)

def getMessagePrefix(message):
    return message.split()[0]

# Returns everything after the first word

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

# Returns a value from a CSV from the first value

def getStoredRowByID(id, file):
    return getStoredRowByN(id, file, 0)
        
# Returns a value from a CSV from the second value

def getStoredRowByQueryID(id, file):
    return getStoredRowByN(id, file, 1)

#Returns a value from a CSV, from a given value

def getStoredRowByN(id, file, n):
    try:
        with open(file) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if row[n] == str(id):
                    return row
            return -1
    except:
        return -1

# Inserts the new N value from a search into a given database

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

# Determines a user's colour and returns it

def getUserColour(message):
    bestColour = "#000000"
    bestRank = 0 
    for role in message.author.roles:
        if role.position > bestRank and str(role.colour) != "#000000":
            bestColour = role.colour
    return bestColour


# Returns the user ID for nickname

def getUserId(user):
    userPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "users.json")
    with open(userPath) as json_file:
        data = json.load(json_file)
        try:
            return data[user]
        except:
            return -1
