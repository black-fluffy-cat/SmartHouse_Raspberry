import datetime
import picamera
from picamera import PiCameraError
import threading

import LedChanger
import utils
from MonitoringPeriodicTask import MonitoringPeriodicTask

__monitoringWorking = False
__camera = None
__currentMonitoringPeriodicTask = None


def onMonitoringStopped():
    global __currentMonitoringPeriodicTask
    if __currentMonitoringPeriodicTask is not None:
        __currentMonitoringPeriodicTask.cancelMonitoringPeriodicTask()
    stopCameraRecording()
    LedChanger.lightPhotoLedOff()
    global __monitoringWorking
    __monitoringWorking = False
    print("Monitoring has been stopped")


def stopCameraRecording():
    global __camera
    if __camera is not None:
        try:
            __camera.stop_recording()
        except Exception as e:
            utils.printException(e)


def makePhoto():
    LedChanger.lightPhotoLedOn()
    _imagePath = None
    global __camera
    if __camera is None:
        __camera = picamera.PiCamera()
    try:
        current_time = datetime.datetime.now()
        from startServer import deviceName
        _imagePath = 'photo/' + str(deviceName) + "_" + str(current_time) + '.jpeg'
        __camera.capture(_imagePath, use_video_port=True)
    except PiCameraError as e:
        LedChanger.lightErrorLedOn()
        utils.printException(e)
    LedChanger.lightPhotoLedOff()
    return _imagePath


def startRecordingAndStreamingAsynchronously():
    global __currentMonitoringPeriodicTask
    if __currentMonitoringPeriodicTask is not None:
        __currentMonitoringPeriodicTask.cancelMonitoringPeriodicTask()
        __currentMonitoringPeriodicTask = None

    __currentMonitoringPeriodicTask = MonitoringPeriodicTask()
    thread = threading.Thread(target=__startRecordingAndStreaming)
    thread.start()


def __startRecordingAndStreaming():
    # Connect a client socket to my_server:8000 (change my_server to the
    # hostname of your server)

    if isMonitoringWorking():
        return
    global __monitoringWorking
    __monitoringWorking = True

    LedChanger.lightPhotoLedOn()
    print("Monitoring has been started")
    try:
        with picamera.PiCamera() as camera:
            global __camera
            __camera = camera
            camera.resolution = (1640, 1232)
            # camera.framerate = 23

            from startServer import deviceName
            videoPath = str(deviceName) + "_" + str(datetime.datetime.now()) + '.h264'
            camera.start_recording(videoPath, resize=(1024, 768))
            __currentMonitoringPeriodicTask.launchMonitoringPeriodicTask(camera)
    except Exception as e:
        utils.printException(e)
        onMonitoringStopped()
    print("__startRecordingAndStreaming finished")


def isMonitoringWorking():
    global __monitoringWorking
    return __monitoringWorking
