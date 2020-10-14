import os
import time
import json

def checkAndCreate(filename, contents):
    path = os.path.join(statsPath,filename + ".csv")
    if not os.path.exists(path):
        f = open(path, "w")
        f.write(str(contents))
        return path
    else:
        return path

def checkAndCreateStats(filename):
    return checkAndCreate(str(filename), str(time.time()) + "\n")

def checkAndCreateTrophy(filename):
    data = getTrophyList()
    string = ""
    for trophy in data.keys():
        string = string + trophy + ",False\n"
    return checkAndCreate(str(filename) + "-trophy", string)

def getTrophyStat(trophyId):
    cacheFile = os.path.join(statsPath, trophyId + ".txt")
    if os.path.isfile(cacheFile) == True:
        with open(cacheFile, "r") as f:
            return str.rstrip(f.read())
    paths = os.listdir(statsPath)
    total = 0
    success = 0
    for path in paths:
        if path.endswith('-trophy.csv') != False:
            total = total + 1
            if getTrophyValue(path[:-11], trophyId) == "True":
                success = success + 1
    if success != 0:
        value = round((success/total)*100)
    else:
        value = 0
    with open(cacheFile, "w") as f:
        f.write(str(value))
    
    return value

def getTrophyList():
    trophyPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trophys.json")
    with open(trophyPath) as json_file:
        data = json.load(json_file)
        return data

def getReadableTrophyList():
    trophys = getTrophyList()
    string = ""
    for key, trophy in trophys.items():
        string = string + trophy['name'] + ": " + trophy['description'] + "\n"
    return string

def checkPlat(userId):
    array = getFileAsArray(checkAndCreateTrophy(userId))
    flag = 1
    for i in range(len(array)):
        identifier = array[i].split(",")[0]
        value = str.rstrip(array[i].split(",")[1])
        if identifier != "plat":
            if str(value) == "False":
                flag = 0
        else:
            if value == "True":
                return 2
    return flag

def editTrophy(userId, trophyId):
    filePath = checkAndCreateTrophy(userId)
    fileArray = getFileAsArray(filePath)
    lineNumber = getStatRow(fileArray, trophyId)
    row = str.rstrip(fileArray[lineNumber]).split(",")
    row[1] = True
    string = ""
    for i in range(len(row)):
        string = string + str(row[i]) + ","
    string = string[:-1] + "\n"
    fileArray[lineNumber] = string
    with open(filePath, "w") as f:
        for line in fileArray:
            f.write(line)
    try:
        os.remove(os.path.join(statsPath, trophyId + ".txt"))
    except:
        return

def editStat(userId, statId):
    filePath = checkAndCreateStats(userId)
    fileArray = getFileAsArray(filePath)
    lineNumber = getStatRow(fileArray, statId)
    row = str.rstrip(fileArray[lineNumber]).split(",")
    row[1] = str(int(row[1]) + 1)
    string = ""
    for i in range(len(row)):
        string = string + str(row[i]) + ","
    string = string[:-1] + "\n"
    fileArray[lineNumber] = string
    with open(filePath, "w") as f:
        for line in fileArray:
            f.write(line)
   
def appendStat(filePath, cmd):
    with open(filePath, "a") as myfile:
        myfile.write(cmd + ",1\n") 
 
def getFileAsArray(filePath):
    f = open(filePath, "r")
    fileArray = []
    for num, line in enumerate(f, 0):
        fileArray.append(line)
    return fileArray

def getStatRow(csvArray, command):
    for i in range(len(csvArray)):
        if csvArray[i].split(",")[0] == command:
            return i
    return -1

def getStatValue(databaseName, command):
    value = getDatabaseValue(databaseName, command, "stat")
    if value == None:
        return -1
    else:
        return int(value)

def getTrophyValue(databaseName, command):
    return getDatabaseValue(str(databaseName), command, "trophy")

def getDatabaseValue(databaseName, command, databaseType):
    databaseName = str(databaseName)
    if databaseType == "trophy":
        csvArray = getFileAsArray(checkAndCreateTrophy(databaseName))
    elif databaseType == "stat":
        csvArray = getFileAsArray(checkAndCreateStats(databaseName))
    else:
        return -1
    try:
        for i in range(len(csvArray)):
            if csvArray[i].split(",")[0] == command:
                return str.rsplit(csvArray[i].split(",")[1])[0]
    except:
        return -1

def writeStat(userId, command):
    filePath = checkAndCreateStats(userId) 
    fileArray = getFileAsArray(filePath)
    statRow = getStatRow(fileArray, command)
    if statRow == -1:
        appendStat(filePath, command)
    else:
        editStat(userId, command)

def getTrophyIcon(tier):
    dictionary = {
        "Bronze":   "https://e7.pngegg.com/pngimages/649/955/png-clipart-playstation-3-playstation-4-achievement-trophy-trophy-game-medal.png",
        "Silver":   "https://www.pngjoy.com/pngs/46/1053381_silver-trophy-playstation-bronze-trophy-transparent-png.png",
        "Gold":     "https://www.pngfind.com/pngs/m/265-2651008_gold-game-playstation-trophy-freetoedit-trophy-ps3-hd.png",
        "Platinum": "https://p7.hiclipart.com/preview/151/962/498/playstation-4-playstation-3-trophy-video-game-xbox-one-platinum.jpg"
    }
    return dictionary[tier]

def testing():
   editTrophy("this", "delete")
   print(str(getTrophyStat('delete')) + "%")
   editTrophy("that", "delete")
   print(str(getTrophyStat('delete')) + "%")
 
statsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"stats")
if not os.path.exists(statsPath):
    os.mkdir(statsPath)

#testing()
