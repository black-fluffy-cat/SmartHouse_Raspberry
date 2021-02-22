import socket


def printException(e):
    print("EXCEPTION : " + repr(e) + " " + str(e))


def isSocketAlive(socketarg):
    if socketarg is None:
        return False
    try:
        return socketarg.fileno() != -1
    except Exception as e:
        printException(e)
        return False


def is_socket_closed(sock: socket.socket) -> bool:
    try:
        # this will try to read bytes without blocking and also without removing them from buffer (peek only)
        data = sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
        if len(data) == 0:
            return True
    except BlockingIOError:
        return False  # socket is open and reading from it would block
    except ConnectionResetError:
        return True  # socket was closed for some other reason
    except Exception as e:
        printException(e)
        return False
    return False
