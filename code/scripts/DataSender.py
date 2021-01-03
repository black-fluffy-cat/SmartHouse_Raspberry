import os
import threading

import requests
import requests as pyrequests

from scripts import DataManager, LedChanger

heartbeatHeaders = {'content-type': 'application/json'}


def makeHeartbeatCall():
    from scripts.startServer import app
    with app.test_request_context():
        try:
            res = pyrequests.post(DataManager.getHeartbeatEndpoint(), headers=heartbeatHeaders,
                                  data=DataManager.getHeartbeatJson())
            if res.status_code != 200:
                LedChanger.lightErrorLedOn()
        except Exception as e:
            LedChanger.lightErrorLedOn()
            print("EXCEPTION : " + repr(e) + " " + str(e))


def sendImage(imageName):
    thread = threading.Thread(target=thread_send_image, args=(imageName,))
    thread.start()


def thread_send_image(imageName):
    try:
        with open(imageName, 'rb') as img:
            imageBasename = os.path.basename(imageName)
            files = {'img': (imageBasename, img, 'multipart/form-data')}
            with requests.Session() as s:
                r = s.post(DataManager.getPhotoReceiveEndpoint(), files=files)
                print(r.status_code)
    except Exception as e:
        print("EXCEPTION : " + repr(e) + " " + str(e))
