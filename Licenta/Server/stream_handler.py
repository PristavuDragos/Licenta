import socket
import threading
import cv2
import numpy as np
import pyaudio
from queue import Queue

local_IP = None
audio_PORT = None
video_PORT = None
UDP_packet_size = None
UDP_video_socket = None
UDP_audio_socket = None
video_data_queue = None
audio_data_queue = None
channels = None
fs = None
sample_format = None
sample_chunk_size = None
frame_width = None
frame_height = None
frame_size = None


def init(settings):
    global local_IP
    global audio_PORT
    global video_PORT
    global UDP_packet_size
    global UDP_video_socket
    global UDP_audio_socket
    global video_data_queue
    global audio_data_queue
    global frame_height
    global frame_width
    global frame_size
    global channels
    global fs
    global sample_format
    global sample_chunk_size
    local_IP = settings["server_IP"]
    audio_PORT = settings["audio_PORT"]
    video_PORT = settings["video_PORT"]
    frame_width = settings["video_default_width"]
    frame_height = settings["video_default_height"]
    UDP_packet_size = settings["UDP_packet_size"]
    channels = settings["audio_channels"]
    fs = settings["audio_fs"]
    sample_chunk_size = settings["audio_sample_chunk_size"]
    sample_format = pyaudio.paInt16
    frame_size = 3 * frame_width * frame_height
    UDP_video_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDP_audio_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    video_data_queue = Queue()
    audio_data_queue = Queue()


def receive_video():
    global UDP_video_socket
    UDP_video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDP_video_socket.bind((local_IP, video_PORT))
    current_timestamp = 0
    while True:
        awaited_packet = 1
        byteMessage = b""
        while len(byteMessage) < frame_size:
            bytesAddressPair = UDP_video_socket.recvfrom(UDP_packet_size)
            header = bytesAddressPair[0][:12].decode().split("\/")
            timestamp = float(header[0])
            packet = int(header[1])
            if packet == 1 and timestamp > current_timestamp:
                byteMessage = b""
                byteMessage += bytesAddressPair[0][12:]
                awaited_packet += 1
                current_timestamp = timestamp
            elif packet == awaited_packet and timestamp == current_timestamp:
                byteMessage += bytesAddressPair[0][12:]
                awaited_packet += 1
            else:
                break
        else:
            byteMessage = byteMessage[:frame_size]
            frame = np.frombuffer(byteMessage, dtype="B").reshape(frame_height, frame_width, 3)
            cv2.imshow('F', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def receive_audio():
    global UDP_audio_socket
    UDP_audio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDP_audio_socket.bind((local_IP, audio_PORT))
    last_timestamp = 0
    while True:
        bytesAddressPair = UDP_audio_socket.recvfrom(UDP_packet_size)
        header = bytesAddressPair[0][:9].decode().split("\/")
        timestamp = float(header[0])
        if last_timestamp < timestamp:
            payload = bytesAddressPair[0][9:]

