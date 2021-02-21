import datetime
import socket
import picamera
from picamera import PiCameraError
import threading

import DataSender
import LedChanger
import utils

shouldStillMonitor = True
monitoringWorking = False


def onMonitoringStopped():
    global shouldStillMonitor
    shouldStillMonitor = False


def makePhoto():
    LedChanger.lightPhotoLedOn()
    imagePath = None
    with picamera.PiCamera() as camera:
        try:
            currentTime = datetime.datetime.now()
            camera.resolution = (2592, 1944)
            from startServer import deviceName
            imagePath = 'photo/' + str(deviceName) + "_" + str(currentTime) + '.jpeg'
            camera.capture(imagePath)
        except PiCameraError as e:
            LedChanger.lightErrorLedOn()
            utils.printException(e)
    LedChanger.lightPhotoLedOff()
    return imagePath


def startRecordingAndStreamingAsynchronously():
    thread = threading.Thread(target=startRecordingAndStreaming)
    thread.start()


def startRecordingAndStreaming():
    # Connect a client socket to my_server:8000 (change my_server to the
    # hostname of your server)

    connection = None
    client_socket = None
    global shouldStillMonitor
    shouldStillMonitor = True
    videoPath = None

    global monitoringWorking
    LedChanger.lightPhotoLedOn()
    try:
        monitoringWorking = True
        with picamera.PiCamera() as camera:
            camera.resolution = (1024, 768)
            camera.framerate = 24
            while shouldStillMonitor:
                if connection is None:
                    client_socket, connection = tryToEstablishStreamConnection()
                # Start recording, sending the output to the connection for 60
                # seconds, then stop
                from startServer import deviceName
                videoPath = str(deviceName) + "_" + str(datetime.datetime.now()) + '.h264'

                camera.start_recording(videoPath)

                try:
                    if connection is not None:
                        camera.start_recording(connection, format='h264', splitter_port=2, resize=(640, 480))
                except Exception as e:
                    utils.printException(e)
                    connection = None
                    client_socket = None

                camera.wait_recording(30)
                camera.stop_recording()

                try:
                    if connection is not None:
                        camera.stop_recording(splitter_port=2)
                except Exception as e:
                    utils.printException(e)
                    connection = None
                    client_socket = None

                DataSender.handleVideoAsynchronously(videoPath)
    finally:
        if connection is not None:
            connection.close()
        if client_socket is not None:
            client_socket.close()
        LedChanger.lightPhotoLedOff()
        monitoringWorking = False
    return videoPath


def tryToEstablishStreamConnection():
    try:
        client_socket = socket.socket()
        from DataManager import defaultServerIP
        client_socket.connect((defaultServerIP, 8000))
        # Make a file-like object out of the connection
        connection = client_socket.makefile('wb')
        print("Connection to stream established")
        return client_socket, connection
    except Exception as e:
        utils.printException(e)
        print("Continuing without connection to stream")
        return None, None


def isMonitoringWorking():
    global monitoringWorking
    return monitoringWorking
