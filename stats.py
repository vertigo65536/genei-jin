import os
import time

def checkAndCreate(filename):
    path = os.path.join(statsPath,filename + ".csv")
    if not os.path.exists(path):
        f = open(path, "w")
        f.write(str(time.time()) + "\n")
        return path
    else:
        return path

def editStat(filePath, fileArray, lineNumber):
    row = str.rstrip(fileArray[lineNumber]).split(",")
    row[1] = str(int(row[1]) + 1)
    string = ""
    for i in range(len(row)):
        string = string + row[i] + ","
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

def searchUserStatValue(userId, command):
    filePath = checkAndCreate(userId)
    flag = 0
    f = open(filePath, "r")
    fileArray = []
    for num, line in enumerate(f, 0):
        fileArray.append(line)
        if str.rstrip(line.split(",")[0]) == command:
            flag = 1
            editNum = num
    if flag == 1:
        return editStat(filePath, fileArray, editNum)
    else:
        return appendStat(filePath, command)

def getStatRow(csvArray, command):
    for i in range(len(csvArray)):
        if csvArray[i].split(",")[0] == command:
            return i
    return -1

def getStatValue(csvArray, command):
    for i in range(len(csvArray)):
        if csvArray[i].split(",")[0] == command:
            return int(str.rsplit(csvArray[i].split(",")[1])[0])

def writeStat(userId, command):
    filePath = checkAndCreate(userId) 
    fileArray = getFileAsArray(filePath)
    statRow = getStatRow(fileArray, command)
    if statRow == -1:
        appendStat(filePath, command)
    else:
        editStat(filePath, fileArray, statRow)

def testing():
    csvPath = checkAndCreate("poop")
    #print(writeStat("poop", "%wiki"))
    print(getStatValue(getFileAsArray("stats/poop.csv"), "%wiki"))
    

statsPath = os.path.join(os.path.dirname(os.path.abspath(__file__)),"stats")
if not os.path.exists(statsPath):
    os.mkdir(statsPath)
