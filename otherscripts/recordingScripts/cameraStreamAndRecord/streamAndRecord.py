#!/usr/bin/env python3
import subprocess
from picamera import PiCamera
import time
#stream_cmd = 'ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i />

stream_cmd = 'ffmpeg -i - -y -hls_time 2 -hls_list_size 10 -start_number 1 mystream.m3u8'

avg = None
stream_pipe = subprocess.Popen(stream_cmd, shell=True, stdin=subprocess.PIPE)
resolution = (320,240)
with PiCamera(resolution = resolution) as camera:

    camera.resolution = (1024, 768)
    camera.framerate = 25
    camera.vflip = True
    camera.hflip = True
    camera.start_recording('myfirstsplitrecording.h264')
    camera.start_recording(stream_pipe.stdin, splitter_port=2, format='h264', bitrate = 6000000)
    camera.wait_recording(30)
    camera.stop_recording()

