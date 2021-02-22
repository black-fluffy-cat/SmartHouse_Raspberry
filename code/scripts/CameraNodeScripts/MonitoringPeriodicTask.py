import threading
import time
import datetime
import socket

import picamera

import DataSender
import utils

__taskLaunched = False
__periodicThread = None

__periodicTaskShouldRun = True

__camera = picamera.PiCamera

__stream_connection = None
__stream_socket = None


def cancelMonitoringPeriodicTask():
    global __periodicTaskShouldRun
    __periodicTaskShouldRun = False


def launchMonitoringPeriodicTask(camera):
    global __camera
    if camera is None:
        return
    __camera = camera

    global __periodicTaskShouldRun
    __periodicTaskShouldRun = True

    global __taskLaunched
    if __taskLaunched:
        return
    __taskLaunched = True

    global __periodicThread
    __periodicThread = threading.Thread(target=__monitoringPeriodicTask)
    __periodicThread.start()


def __monitoringPeriodicTask():
    while __periodicTaskShouldRun:
        _videoPath = __splitCurrentRecording()
        DataSender.handleVideoAsynchronously(_videoPath)
        startToStreamStartTime = time.time()
        __tryToStreamMonitoring()
        startToStreamExecutionTime = time.time() - startToStreamStartTime
        if startToStreamExecutionTime < 30:
            time.sleep(30 - startToStreamExecutionTime)
    __onDestroyTask()
    global __taskLaunched
    __taskLaunched = False
    print("MonitoringPeriodicTask has just quit")


def __splitCurrentRecording():
    try:
        from startServer import deviceName
        _videoPath = str(deviceName) + "_" + str(datetime.datetime.now()) + '.h264'

        __camera.split_recording(_videoPath)
        return _videoPath
    except Exception as e:
        utils.printException(e)
        return None


def __tryToStreamMonitoring():
    global __stream_connection
    global __stream_socket

    if __stream_connection is None or not utils.isSocketAlive(__stream_socket):
        if not utils.isSocketAlive(__stream_socket):
            __stopCameraMonitoringStreaming()
        __stream_connection, __stream_socket = __tryToEstablishStreamConnection()

    if __stream_connection is not None:
        __startCameraMonitoringStreaming()


def __tryToEstablishStreamConnection():
    try:
        client_socket = socket.socket()
        client_socket.settimeout(20)
        from DataManager import defaultServerIP
        client_socket.connect((defaultServerIP, 8000))
        # Make a file-like object out of the connection
        connection = client_socket.makefile('wb')
        print("Connection to stream established")
        return connection, client_socket
    except Exception as e:
        utils.printException(e)
        print("Continuing without connection to stream")
        return None, None


def __startCameraMonitoringStreaming():
    global __stream_connection
    global __camera
    try:
        __camera.start_recording(__stream_connection, format='h264', splitter_port=2, resize=(640, 480))
    except Exception as e:
        utils.printException(e)
        __onDestroyTask()


def __stopCameraMonitoringStreaming():
    try:
        global __camera
        __camera.stop_recording(splitter_port=2)
    except Exception as e:
        utils.printException(e)


def __onDestroyTask():
    global __stream_connection
    global __stream_socket
    if __stream_socket is not None:
        try:
            __stopCameraMonitoringStreaming()
            __stream_socket.close()
            __stream_connection = None
            __stream_socket = None
        except Exception as e:
            utils.printException(e)
