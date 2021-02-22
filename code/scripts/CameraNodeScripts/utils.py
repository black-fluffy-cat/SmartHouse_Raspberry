import socket


def printException(e):
    print("EXCEPTION : " + repr(e) + " " + str(e))


def isSocketAlive(socketarg):
    if socketarg is None:
        return False
    try:
        return socket.socket(socketarg).fileno() != -1
    except Exception as e:
        printException(e)
        return False
