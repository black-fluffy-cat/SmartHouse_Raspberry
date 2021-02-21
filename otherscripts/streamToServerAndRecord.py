import socket
import time
import picamera

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket()
client_socket.connect(('192.168.43.157', 8000))

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
number = 0
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (1024, 768)
        camera.framerate = 24
        while True:
                # Start recording, sending the output to the connection for 60
                # seconds, then stop
                camera.start_recording('highres' + str(number) + '.h264')
                number = number + 1
                camera.start_recording(connection, format='h264', splitter_port=2, resize=(640, 480))
                camera.wait_recording(30)
                camera.stop_recording()
                camera.stop_recording(splitter_port=2)
finally:
    connection.close()
    client_socket.close()
