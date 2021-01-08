import time
import os
import json

from scripts import utils

current_ms_time = lambda: int(round(time.time() * 1000))

lastKnownServerAddressFileName = "lastKnownServerAddress.txt"
defaultServerAddress = "http://192.168.0.107:8080"
serverUrl = defaultServerAddress


def getHeartbeatEndpoint():
    return str(serverUrl) + "/heartbeat"


def getAlertEndpoint():
    return str(serverUrl) + "/alert"


def getPhotoReceiveEndpoint():
    return str(serverUrl) + "/receivePhoto"


def getNgrokAddressesEndpoint():
    return str(serverUrl) + "/receiveNgrokAddresses"


def getHeartbeatJson():
    from scripts.startServer import startTime
    from scripts.startServer import lastAlertTime
    from scripts.startServer import deviceName
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


def onServerAddressReceived(serverAddress):
    global serverUrl
    serverUrl = serverAddress
    saveServerAddress(serverAddress)


def getServerAddress():
    return serverUrl


def saveServerAddress(serverAddress):
    try:
        with open(lastKnownServerAddressFileName, 'w') as file:
            file.write(serverAddress)
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
    serverUrl = defaultServerAddress


def getNgrokAddressesAsJson():
    os.system("curl  http://localhost:4040/api/tunnels > tunnels.json")

    listOfTunnels = []

    with open('tunnels.json') as data_file:
        datajson = json.load(data_file)

    for tunnel in datajson['tunnels']:
        tunnelJson = {'name': tunnel['name'], 'publicUrl': tunnel['public_url'], 'addr': tunnel['config']['addr']}
        listOfTunnels.append(tunnelJson)

    objectToSend = {'senderId': "PC", 'tunnelsList': listOfTunnels}
    return json.dumps(objectToSend)
