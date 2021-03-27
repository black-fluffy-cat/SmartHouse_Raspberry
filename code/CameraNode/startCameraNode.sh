#!/bin/sh

cd /home/pi/Desktop/smarthouse_projects/SmartHouse_Raspberry/code/CameraNode
export FLASK_APP=/home/pi/Desktop/smarthouse_projects/SmartHouse_Raspberry/code/CameraNode/src/startServer.py
flask run --host=0.0.0.0
