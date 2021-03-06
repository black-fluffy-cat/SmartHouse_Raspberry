import threading
import time
import datetime
import socket

import DataSender
import utils


class MonitoringPeriodicTask:
    def __init__(self):
        self.__task_launched = False
        self.__periodic_thread = None

        self.__periodic_task_should_Run = True

        self.__camera = None
        self.__previous_monitoring_video_path = None

        self.__stream_connection = None
        self.__stream_socket = None

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
        should_retry_stream = False

        if self.__stream_connection is None or utils.is_socket_closed(self.__stream_socket):
            if not utils.isSocketAlive(self.__stream_socket):
                self.__stopCameraMonitoringStreaming()
            self.__stream_connection, self.__stream_socket = self.__tryToEstablishStreamConnection()
            should_retry_stream = True

        if self.__stream_connection is not None and should_retry_stream:
            self.__startCameraMonitoringStreaming()

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
            self.__camera.start_recording(self.__stream_connection, format='h264', splitter_port=2, resize=(640, 480))
        except Exception as e:
            utils.printException(e)
            self.__onDestroyTask()

    def __stopCameraMonitoringStreaming(self):
        try:
            self.__camera.stop_recording(splitter_port=2)
        except Exception as e:
            utils.printException(e)

    def __onDestroyTask(self):
        if self.__stream_socket is not None:
            try:
                self.__stopCameraMonitoringStreaming()
                self.__stream_socket.close()
                self.__stream_connection = None
                self.__stream_socket = None
            except Exception as e:
                utils.printException(e)
