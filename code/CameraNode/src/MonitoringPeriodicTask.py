import datetime
import io
import logging
import socketserver
import threading
import time
from http import server
from threading import Condition

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

        self.__periodic_task_should_run = True

        self.__camera = None
        self.__previous_monitoring_video_path = None

        self.__streaming_stopped = True

    def cancelMonitoringPeriodicTask(self):
        self.__periodic_task_should_run = False

    def launchMonitoringPeriodicTask(self, camera, video_path):
        if camera is None:
            return
        self.__camera = camera

        self.__previous_monitoring_video_path = video_path
        self.__periodic_task_should_run = True

        if self.__task_launched:
            return
        self.__task_launched = True

        self.__periodic_thread = threading.Thread(target=self.__monitoringPeriodicTask())
        self.__periodic_thread.start()

    def __monitoringPeriodicTask(self):
        while self.__periodic_task_should_run:
            try:
                _video_path = self.__splitCurrentRecording()
                DataSender.handleVideoAsynchronously(_video_path)
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
            from DataManager import deviceName, videoDir
            _video_path = str(videoDir) + str(deviceName) + "_" + str(datetime.datetime.now()) + '.h264'

            self.__camera.split_recording(_video_path)
            path_to_return = self.__previous_monitoring_video_path
            self.__previous_monitoring_video_path = _video_path
            return path_to_return
        except Exception as e:
            utils.printException(e)
            return None

    def __tryToStreamMonitoring(self):
        if self.__streaming_stopped:
            self.__streaming_stopped = False
            self.__startCameraMonitoringStreaming()

    def __startCameraMonitoringStreaming(self):
        try:
            global output
            self.__camera.start_recording(output, format='mjpeg', splitter_port=2, resize=(640, 480))
            address = ('', 8000)
            stream_server = StreamingServer(address, StreamingHandler)
            stream_server.serve_forever()
        except Exception as e:
            self.__streaming_stopped = True
            utils.printException(e)
            self.__onDestroyTask()

    def __stopCameraMonitoringStreaming(self):
        try:
            self.__camera.stop_recording(splitter_port=2)
        except Exception as e:
            utils.printException(e)
        self.__streaming_stopped = True

    def __onDestroyTask(self):
        try:
            self.__stopCameraMonitoringStreaming()
        except Exception as e:
            utils.printException(e)

from DataManager import deviceName
PAGE = """\
<html>
<head>
<title>""" + str(deviceName) + """</title>
</head>
<body>
<center><h1>""" + str(deviceName) + """</h1></center>
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
                    global output
                    with output.condition:
                        output.condition.wait()
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
