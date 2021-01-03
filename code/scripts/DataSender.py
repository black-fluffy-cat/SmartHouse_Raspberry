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
