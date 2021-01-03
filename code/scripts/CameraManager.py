import picamera
import datetime

from picamera import PiCameraError

from scripts import LedChanger


def makePhoto():
    LedChanger.lightPhotoLedOn()
    with picamera.PiCamera() as camera:
        try:
            currentTime = datetime.datetime.now()
            camera.resolution = (2592, 1944)
            imageName = 'photo/' + str(currentTime) + '.jpeg'
            camera.capture(imageName)
        except PiCameraError as e:
            LedChanger.lightErrorLedOn()
            print("EXCEPTION : " + repr(e) + " " + str(e))
    LedChanger.lightPhotoLedOff()
