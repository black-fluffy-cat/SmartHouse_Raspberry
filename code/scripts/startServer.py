# !/usr/bin/python

import RPi.GPIO as GPIO
from flask import request
from flask_api import FlaskAPI

from scripts import CameraManager, HeartbeatManager, LedChanger, DataSender, DataManager
from scripts.DataManager import current_ms_time

deviceName = "RPI Zero + Camera"

GPIO.setmode(GPIO.BCM)
LedChanger.initLedChanger()

app = FlaskAPI(__name__)

lastAlertTime = 0


@app.route('/alertPhoto', methods=["POST"])
def alertPhoto():
    if request.method == "POST":
        onAlertPhotoRequest()
        return {"result": "OK"}
    else:
        return {"result": "FAIL"}


def onAlertPhotoRequest():
    global lastAlertTime
    lastAlertTime = current_ms_time()
    imagePath = CameraManager.makePhoto()
    DataSender.handleImage(imagePath)


@app.route('/led/<color>/', methods=["GET", "POST"])
def api_leds_control(color):
    if request.method == "POST":
        from scripts.LedChanger import LEDS
        if color in LEDS:
            GPIO.output(LEDS[color], int(request.data.get("state")))
    return {color: GPIO.input(LEDS[color])}


@app.route('/setServerUrl/', methods=["POST"])
def setServerUrl():
    if request.method == "POST":
        # if field is none or exception occurred then do not set it
        DataManager.onServerAddressReceived(request.data.get("serverUrl"))
        return {"result": "OK"}
    return {"result": "FAIL"}


print('Application starting')
app.run()
startTime = current_ms_time()
DataManager.refreshServerAddressFromFile()
HeartbeatManager.initHeartbeatThread()
