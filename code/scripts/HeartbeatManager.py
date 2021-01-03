import time
import threading

from scripts import DataSender


def initHeartbeatThread():
    print('Init heartbeat loop')
    thread = threading.Thread(target=heartbeatLoop)
    thread.start()

def heartbeatLoop():
    while True:
        DataSender.makeHeartbeatCall()
        time.sleep(30)
