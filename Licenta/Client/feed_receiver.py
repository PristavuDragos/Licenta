import math
import socket
import threading
from queue import Queue

import main_GUI
import pyaudio
import main_client

local_IP = None
UDP_packet_size = None
UDP_payload_size = None
UDP_video_socket = None
UDP_audio_socket = None
video_data_frames = None
video_packet_queue = None
audio_data_queue = None
channels = None
fs = None
sample_format = None
sample_chunk_size = None
frame_width = None
frame_height = None
frame_size = None
audio_receiver_on = None
video_receiver_on = None
packets_per_frame = None


def init(settings):
    global local_IP
    global UDP_packet_size
    global UDP_payload_size
    global UDP_video_socket
    global UDP_audio_socket
    global video_data_frames
    global audio_data_queue
    global frame_height
    global frame_width
    global frame_size
    global channels
    global fs
    global sample_format
    global sample_chunk_size
    global packets_per_frame
    global video_packet_queue
    video_packet_queue = Queue()
    local_IP = settings["server_IP"]
    frame_width = settings["video_default_width"]
    frame_height = settings["video_default_height"]
    UDP_packet_size = settings["UDP_packet_size"]
    UDP_payload_size = settings["UDP_payload_size"]
    channels = settings["audio_channels"]
    fs = settings["audio_fs"]
    sample_chunk_size = settings["audio_sample_chunk_size"]
    sample_format = pyaudio.paInt16
    frame_size = 3 * frame_width * frame_height
    packets_per_frame = math.ceil(frame_size / UDP_payload_size)
    UDP_video_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDP_audio_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    video_data_frames = {}


def process_video_packets(**signals):
    global video_data_frames
    global video_packet_queue
    while video_receiver_on:
        if not video_packet_queue.empty():
            packet = video_packet_queue.get()
            header = packet[0][:23].decode().split("\/")
            timestamp = float(header[0])
            packet_number = int(header[1])
            client_id = header[2]
            packets_per_frame_ = int(header[3])
            if client_id in video_data_frames:
                frame_data = video_data_frames[client_id]
                if packet_number == 1 and timestamp > frame_data[1]:
                    payload = b""
                    payload += packet[0][23:]
                    video_data_frames[client_id] = [payload, timestamp, packet_number]
                    if packet_number == packets_per_frame_:
                        signals["send_data"].emit(((video_data_frames.pop(client_id))[0], client_id))
                elif packet_number == frame_data[2] + 1 and timestamp == frame_data[1]:
                    frame_data[0] += packet[0][23:]
                    frame_data[2] = packet_number
                    if packet_number == packets_per_frame_:
                        signals["send_data"].emit((frame_data[0], client_id))
                        del video_data_frames[client_id]
                    else:
                        video_data_frames[client_id] = frame_data
                else:
                    del video_data_frames[client_id]
            else:
                if packet_number == 1:
                    payload = b""
                    payload += packet[0][23:]
                    video_data_frames[client_id] = [payload, timestamp, packet_number]
                    if packet_number == packets_per_frame_:
                        signals["send_data"].emit(((video_data_frames.pop(client_id))[0], client_id))


def process_audio_packets(packet):
    pass


def receive_video():
    while video_receiver_on:
        try:
            video_packet_queue.put(UDP_video_socket.recvfrom(UDP_packet_size))
        except:
            pass


def receive_audio():
    while audio_receiver_on:
        try:
            process_audio_packets(UDP_audio_socket.recvfrom(UDP_packet_size))
        except:
            pass


def stop_audio_receiver():
    global audio_receiver_on
    audio_receiver_on = False


def stop_video_receiver():
    global video_receiver_on
    video_receiver_on = False


def start_audio_receiver():
    global audio_receiver_on
    global UDP_audio_socket
    UDP_audio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDP_audio_socket.bind((local_IP, 0))
    UDP_audio_socket.settimeout(5)
    audio_handler_thread = threading.Thread(target=receive_audio)
    audio_receiver_on = True
    audio_handler_thread.start()
    return UDP_audio_socket.getsockname()


def start_video_receiver():
    global video_receiver_on
    global UDP_video_socket
    UDP_video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    UDP_video_socket.bind((local_IP, 0))
    UDP_video_socket.settimeout(5)
    video_handler_thread = threading.Thread(target=receive_video)
    video_receiver_on = True
    video_handler_thread.start()
    return UDP_video_socket.getsockname()


def start_feed_receiver(settings):
    init(settings)
    return start_video_receiver(), start_audio_receiver()
