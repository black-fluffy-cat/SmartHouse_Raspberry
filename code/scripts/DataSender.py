import os
import threading

import requests as pyrequests

from scripts import DataManager, LedChanger, utils

jsonHeaders = {'content-type': 'application/json'}


def makeHeartbeatCall():
    from scripts.startServer import app
    with app.test_request_context():
        try:
            res = pyrequests.post(DataManager.getHeartbeatEndpoint(), headers=jsonHeaders,
                                  data=DataManager.getHeartbeatJson())
            if res.status_code != 200:
                LedChanger.lightErrorLedOn()
        except Exception as e:
            LedChanger.lightErrorLedOn()
            utils.printException(e)


def makeNgrokAddressesCall():
    from scripts.startServer import app
    with app.test_request_context():
        try:
            res = pyrequests.post(DataManager.getNgrokAddressesEndpoint(), headers=jsonHeaders,
                                  data=DataManager.getNgrokAddressesAsJson(), timeout=10)
            if res.status_code != 200:
                LedChanger.lightErrorLedOn()
                return False
            return True
        except Exception as e:
            LedChanger.lightErrorLedOn()
            utils.printException(e)
            return False


def handleImage(imagePath):
    thread = threading.Thread(target=thread_handle_sending_and_deleting_image, args=(imagePath,))
    thread.start()


def thread_handle_sending_and_deleting_image(imagePath):
    try:
        with open(imagePath, 'rb') as img:
            imageBasename = os.path.basename(imagePath)
            files = {'img': (imageBasename, img, 'multipart/form-data')}
            with pyrequests.Session() as s:
                r = s.post(DataManager.getPhotoReceiveEndpoint(), files=files)
                print(r.status_code)
                if r.status_code == 200:
                    DataManager.deleteFile(imagePath)
    except Exception as e:
        utils.printException(e)
