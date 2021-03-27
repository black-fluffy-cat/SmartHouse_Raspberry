import json
import os
import time

import utils
import psutil

current_ms_time = lambda: int(round(time.time() * 1000))
lastKnownServerAddressFileName = "lastKnownServerAddress.txt"

deviceName = ""
serverIP = ""
serverPort = ""
serverUrl = ""

videoDir="vid/"
photoDir="photo/"

diskUsagePercentageThreshold = 95
defaultNumberOfVideosToRemove = 10

def createServerUrl():
    return "http://" + str(serverIP) + ":" + str(serverPort)


def loadDataFromConfig():
    import ConfigLoader
    global deviceName, serverIP, serverPort, serverUrl

    deviceName, serverIP, serverPort = ConfigLoader.loadConfig()
    serverUrl = createServerUrl()


def getHeartbeatEndpoint():
    return str(serverUrl) + "/heartbeat"


def getAlertEndpoint():
    return str(serverUrl) + "/alert"


def getPhotoReceiveEndpoint():
    return str(serverUrl) + "/receivePhoto"


def getNgrokAddressesEndpoint():
    return str(serverUrl) + "/receiveNgrokAddresses"


def getVideoReceiveEndpoint():
    return str(serverUrl) + "/receiveVideo"


def getHeartbeatJson():
    from startServer import startTime
    from startServer import lastAlertTime
    currentTime = current_ms_time()
    timeFromStart = currentTime - startTime
    timeFromAlert = currentTime - lastAlertTime
    firstPart = "{\"deviceName\":\""
    secondPart = "\",\"timeFromStart\":\""
    timeFromStartString = str(timeFromStart)
    thirdPart = "\",\"timeFromAlert\":\""
    timeFromAlertString = str(timeFromAlert)
    fourthPart = "\"}"
    return firstPart + deviceName + secondPart + timeFromStartString + thirdPart + timeFromAlertString + fourthPart


def deleteFile(filepath):
    try:
        import os
        os.remove(filepath)
    except Exception as e:
        utils.printException(e)


def onServerAddressReceived(newServerUrl):
    global serverUrl
    serverUrl = newServerUrl
    saveServerAddress(newServerUrl)


def getServerAddress():
    return serverUrl


def saveServerAddress(newServerUrl):
    try:
        with open(lastKnownServerAddressFileName, 'w') as file:
            file.write(newServerUrl)
    except Exception as e:
        utils.printException(e)


def refreshServerAddressFromFile():
    global serverUrl
    try:
        with open(lastKnownServerAddressFileName, 'r') as file:
            serverUrl = file.readline()
            return
    except Exception as e:
        utils.printException(e)


def getNgrokAddressesAsJson():
    os.system("curl  http://localhost:4040/api/tunnels > tunnels.json")

    listOfTunnels = []

    with open('tunnels.json') as data_file:
        datajson = json.load(data_file)

    for tunnel in datajson['tunnels']:
        tunnelJson = {'name': tunnel['name'], 'publicUrl': tunnel['public_url'], 'addr': tunnel['config']['addr']}
        listOfTunnels.append(tunnelJson)

    objectToSend = {'senderId': str(deviceName), 'tunnelsList': listOfTunnels}
    return json.dumps(objectToSend)

def removeOldestVideos(numberOfVideos):
    list_of_files = os.listdir(str(videoDir))
    full_path = [str(videoDir) + "{0}".format(x) for x in list_of_files]

    for _ in range(0, numberOfVideos):
        try:
            oldest_file = min(full_path, key=os.path.getctime)
            os.remove(oldest_file)
            full_path.remove(oldest_file)
        except Exception as e:
            utils.printException(e)


def makeStorageCheck():
    usedDiskPercentage = psutil.disk_usage('/').percent
    if usedDiskPercentage > diskUsagePercentageThreshold:
        removeOldestVideos(defaultNumberOfVideosToRemove)
    # TODO Send info to server about amount of disk space