import picamera
import datetime
import requests
import threading
import os
import time

recordingTime = 5
url = 'http://192.168.0.108:8080/monitoring/uploadImage'

def thread_send_image(imageName):
	with open(imageName, 'rb') as img:
		imageBasename = os.path.basename(imageName)
		files = {'img': (imageBasename, img, 'multipart/form-data') }
		with requests.Session() as s:
			r = s.post(url, files = files)
			print(r.status_code)

with picamera.PiCamera() as camera:
	currentTime = datetime.datetime.now()
	print("ABAB Hello at beginning " + str(currentTime))
	for i in range(1, 10000):
		try:
			currentTime = datetime.datetime.now()
			print("ABAB Loop %d start" % i)
#			camera.start_recording(str(currentTime) + ' %d.h264' % i)
#			print("ABAB Loop %d before wait recording" % i)
#			camera.wait_recording(recordingTime)
#			print("ABAB Loop %d before stop recording" % i)
#			camera.stop_recording()
			print("ABAB Loop %d before setting image resolution" % i)
			camera.resolution = (2592, 1944)
			print("ABAB Loop %d before setting image capture" % i)
			imageName = str(currentTime) + ' %d.jpeg' % i
			camera.capture(imageName)
			print("ABAB Loop %d before thread creation" % i)
			thread = threading.Thread(target=thread_send_image, args = (imageName,))
			print("ABAB Loop %d before thread start" % i)
			thread.start()
#			print("ABAB Loop %d before setting video resolution" % i)
#			camera.resolution = (640, 480)
			print("ABAB Loop %d end" % i)
			time.sleep(1)
		except PiCameraError as e:
			print("EXCEPTION : " + repr(e) + " " + str(e))
	print("ABAB Script finish" % i)
#	camera.stop_recording()
