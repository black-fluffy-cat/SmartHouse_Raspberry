# !/usr/bin/python

import RPi.GPIO as GPIO
from flask import request
from flask_api import FlaskAPI

import CameraManager
import DataManager
import DataSender
import HeartbeatManager
import LedChanger
import NgrokAddressesManager
from DataManager import current_ms_time

photoButtonPin = 17  # Move to common place with LEDS pins

GPIO.setmode(GPIO.BCM)
GPIO.setup(photoButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

LedChanger.initLedChanger()

app = FlaskAPI(__name__)

lastAlertTime = 0


def photoButtonEvent(channel):
    if GPIO.input(photoButtonPin) == GPIO.HIGH:
        CameraManager.makePhoto()


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
    DataSender.handleImageAsynchronously(imagePath)


@app.route('/led/<color>/', methods=["GET", "POST"])
def api_leds_control(color):
    if request.method == "POST":
        from LedChanger import LEDS
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


@app.route('/startMonitoring', methods=["POST"])
def startMonitoring():
    if request.method == "POST":
        # if field is none or exception occurred then do not set it
        onStartMonitoringRequest()
        return {"result": "OK"}
    return {"result": "FAIL"}


def onStartMonitoringRequest():
    CameraManager.startRecordingAndStreamingAsynchronously()


@app.route('/stopMonitoring', methods=["POST"])
def stopMonitoring():
    if request.method == "POST":
        # if field is none or exception occurred then do not set it
        CameraManager.onMonitoringStopped()
        return {"result": "OK"}
    return {"result": "FAIL"}


@app.route('/isMonitoringWorking', methods=["GET"])
def isMonitoringWorking():
    return {"result": str(CameraManager.isMonitoringWorking())}


print('Application starting')
app.run()
startTime = current_ms_time()

DataManager.loadDataFromConfig()
DataManager.refreshServerAddressFromFile()
HeartbeatManager.initHeartbeatThread()
# NgrokAddressesManager.sendAddressesToServerUntilSuccess()

GPIO.add_event_detect(photoButtonPin, GPIO.BOTH, callback=photoButtonEvent)
