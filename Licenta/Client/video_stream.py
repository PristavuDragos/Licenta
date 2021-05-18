import math
import time
import cv2
import imutils
import threading
import main_client
from Utils import functions

UDP_packet_size = None
UDP_payload_size = None
server_PORT = None
server_IP = None
video_PORT = None
frame_width = None
frame_height = None
sender_socket = None
feed_is_on = None
client_id = None


def init(settings, address):
    global UDP_packet_size
    global server_PORT
    global video_PORT
    global server_IP
    global sender_socket
    global feed_is_on
    global frame_width
    global frame_height
    global client_id
    global UDP_payload_size
    client_id = main_client.client_id
    feed_is_on = False
    UDP_packet_size = settings["UDP_packet_size"]
    UDP_payload_size = settings["UDP_payload_size"]
    server_PORT = settings["server_PORT"]
    video_PORT = address[1]
    server_IP = address[0]
    frame_width = settings["video_default_width"]
    frame_height = settings["video_default_height"]
    sender_socket = main_client.sender_socket


def video_feed():
    capture = cv2.VideoCapture(0)
    initial_time = time.perf_counter()
    while feed_is_on:
        ret, frame = capture.read()
        frame = imutils.resize(frame, width=frame_width, height=frame_height)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        timestamp = str(time.perf_counter() - initial_time)[0:7]
        byteImage = frame.tobytes()
        image_chunks = functions.split_into_chunks(byteImage, UDP_payload_size)
        chunk_order_number = 1
        packets_per_frame = math.ceil(len(byteImage) / UDP_payload_size)
        for chunk in image_chunks:
            header = bytes(timestamp + "\\/" + str(chunk_order_number) + "\\/" + client_id + "\\/"
                           + str(packets_per_frame) + "\\/", "utf-8")
            sender_socket.sendto(header + chunk, (server_IP, video_PORT))
            chunk_order_number += 1
            time.sleep(0.025)
        if cv2.waitKey(1) & 0xFF == ord('q') or not feed_is_on:
            break
    capture.release()


def video_feed_test():
    initial_time = time.perf_counter()
    current_frame = 0
    while feed_is_on:
        frame = cv2.imread("../Assets/GIF_Feed/frame_" + str(current_frame) + ".jpg")
        current_frame = (current_frame + 1) % 35
        frame = cv2.resize(frame, (frame_width, frame_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        timestamp = str(time.perf_counter() - initial_time)[0:7]
        byteImage = frame.tobytes()
        image_chunks = functions.split_into_chunks(byteImage, UDP_payload_size)
        chunk_order_number = 1
        packets_per_frame = math.ceil(len(byteImage) / UDP_payload_size)
        for chunk in image_chunks:
            header = bytes(timestamp + "\\/" + str(chunk_order_number) + "\\/" + client_id + "\\/"
                           + str(packets_per_frame) + "\\/", "utf-8")
            sender_socket.sendto(header + chunk, (server_IP, video_PORT))
            chunk_order_number += 1
            time.sleep(0.05)
        if not feed_is_on:
            break


def start_video_feed():
    global feed_is_on
    video_thread = threading.Thread(target=video_feed)
    feed_is_on = True
    video_thread.start()
#    video_thread.join()


def start_video_feed_test():
    global feed_is_on
    video_thread = threading.Thread(target=video_feed_test)
    feed_is_on = True
    video_thread.start()


def stop_video_feed():
    global feed_is_on
    feed_is_on = False
