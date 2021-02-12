import picamera
import datetime

with picamera.PiCamera() as camera:
    currentTime = datetime.datetime.now()
    camera.resolution = (640, 480)
    camera.start_recording(str(currentTime) + ' 1.h264')
    camera.wait_recording(5)
    camera.stop_recording()
    camera.resolution = (2592, 1944)
    camera.capture(str(currentTime) + ' 1.jpeg')
    camera.resolution = (640, 480)
    for i in range(2, 10000):
        currentTime = datetime.datetime.now()
        camera.start_recording(str(currentTime) + ' %d.h264' % i)
        camera.wait_recording(5)
        camera.stop_recording()
        camera.resolution = (2592, 1944)
        camera.capture(str(currentTime) + ' %d.jpeg' % i)
        camera.resolution = (640, 480)
    camera.stop_recording()
