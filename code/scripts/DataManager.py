import time

from scripts import utils

current_ms_time = lambda: int(round(time.time() * 1000))


def getHeartbeatEndpoint():
    from scripts.startServer import serverUrl
    return str(serverUrl) + "/heartbeat"


def getAlertEndpoint():
    from scripts.startServer import serverUrl
    return str(serverUrl) + "/alert"


def getPhotoReceiveEndpoint():
    from scripts.startServer import serverUrl
    return str(serverUrl) + "/receivePhoto"


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


