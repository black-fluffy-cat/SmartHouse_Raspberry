import threading
import time
import datetime
import socket

import io
import logging
import socketserver
from threading import Condition
from http import server

import DataSender
import utils

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

output = StreamingOutput()

class MonitoringPeriodicTask:
    def __init__(self):
        self.__task_launched = False
        self.__periodic_thread = None

        self.__periodic_task_should_Run = True

        self.__camera = None
        self.__previous_monitoring_video_path = None

        self.__stream_connection = None
        self.__stream_socket = None

        self.__streamingStopped = True

    def cancelMonitoringPeriodicTask(self):
        self.__periodic_task_should_Run = False

    def launchMonitoringPeriodicTask(self, camera, videoPath):
        if camera is None:
            return
        self.__camera = camera

        self.__previous_monitoring_video_path = videoPath
        self.__periodic_task_should_Run = True

        if self.__task_launched:
            return
        self.__task_launched = True

        self.__periodic_thread = threading.Thread(target=self.__monitoringPeriodicTask())
        self.__periodic_thread.start()

    def __monitoringPeriodicTask(self):
        while self.__periodic_task_should_Run:
            try:
                _videoPath = self.__splitCurrentRecording()
                DataSender.handleVideoAsynchronously(_videoPath)
                start_to_stream_start_time = time.time()
                self.__tryToStreamMonitoring()
                start_to_stream_execution_time = time.time() - start_to_stream_start_time
                if start_to_stream_execution_time < 30:
                    time.sleep(30 - start_to_stream_execution_time)
            except Exception as e:
                utils.printException(e)
        self.__onDestroyTask()
        self.__task_launched = False
        print("MonitoringPeriodicTask has just quit")

    def __splitCurrentRecording(self):
        try:
            from startServer import deviceName
            _video_path = str(deviceName) + "_" + str(datetime.datetime.now()) + '.h264'

            self.__camera.split_recording(_video_path)
            path_to_return = self.__previous_monitoring_video_path
            self.__previous_monitoring_video_path = _video_path
            return path_to_return
        except Exception as e:
            utils.printException(e)
            return None

    def __tryToStreamMonitoring(self):
        if self.__streamingStopped:
            self.__streamingStopped = False
            self.__startCameraMonitoringStreaming()
        # should_retry_stream = False
        #
        # if self.__stream_connection is None or utils.is_socket_closed(self.__stream_socket):
        #     if not utils.isSocketAlive(self.__stream_socket):
        #         self.__stopCameraMonitoringStreaming()
        #     self.__stream_connection, self.__stream_socket = self.__tryToEstablishStreamConnection()
        #     should_retry_stream = True
        #
        # if self.__stream_connection is not None and should_retry_stream:
        #     self.__startCameraMonitoringStreaming()

    def __tryToEstablishStreamConnection(self):
        try:
            client_socket = socket.socket()
            client_socket.settimeout(20)
            from DataManager import defaultServerIP
            client_socket.connect((defaultServerIP, 8000))
            # Make a file-like object out of the connection
            connection = client_socket.makefile('wb')
            print("Connection to stream established")
            return connection, client_socket
        except Exception as e:
            utils.printException(e)
            print("Continuing without connection to stream")
            return None, None

    def __startCameraMonitoringStreaming(self):
        try:
            self.__camera.start_recording(output, format='mjpeg', splitter_port=2, resize=(640, 480))
            address = ('', 8000)
            stream_server = StreamingServer(address, StreamingHandler)
            stream_server.serve_forever()
        except Exception as e:
            self.__streamingStopped = True
            utils.printException(e)
            self.__onDestroyTask()

    def __stopCameraMonitoringStreaming(self):
        try:
            self.__camera.stop_recording(splitter_port=2)
        except Exception as e:
            utils.printException(e)
        self.__streamingStopped = True

    def __onDestroyTask(self):
        if self.__stream_socket is not None:
            try:
                self.__stopCameraMonitoringStreaming()
                self.__stream_socket.close()
                self.__stream_connection = None
                self.__stream_socket = None
            except Exception as e:
                utils.printException(e)

# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

PAGE="""\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    global vidOutput
                    with vidOutput.condition:
                        vidOutput.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True