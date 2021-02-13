import datetime

import picamera
from picamera import PiCameraError

import LedChanger
import utils


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
