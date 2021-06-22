import math
import socket
import threading

import pyaudio
from queue import Queue
from Utils import functions


class StreamHandler:
    def __init__(self, settings, meeting_session):
        self.video_receiver_on = True
        self.audio_receiver_on = True
        self.meeting_session = meeting_session
        self.local_IP = settings["server_IP"]
        self.frame_width = settings["video_default_width"]
        self.frame_height = settings["video_default_height"]
        self.UDP_packet_size = settings["UDP_packet_size"]
        self.UDP_payload_size = settings["UDP_payload_size"]
        self.channels = settings["audio_channels"]
        self.fs = settings["audio_fs"]
        self.sample_chunk_size = settings["audio_sample_chunk_size"]
        self.sample_format = pyaudio.paInt16
        self.frame_size = 3 * self.frame_width * self.frame_height
        self.packets_per_frame = math.ceil(self.frame_size / self.UDP_payload_size)
        self.UDP_video_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDP_audio_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.stream_sender_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.video_data_frames = {}
        self.video_packet_queue = Queue()
        self.audio_data_queue = Queue()

    def send_audio_to_participants(self, packet):
        participants = self.meeting_session.participants
        header = packet[:35].decode().split("\/")
        timestamp = header[0]
        sender = header[1]
        payload = packet[35:]
        try:
            for client_id, client_addresses in participants.items():
                if client_id != sender:
                    address = client_addresses[1]
                    while len(timestamp) < 7:
                        timestamp = timestamp + "0"
                    header = bytes(str(timestamp) + "\\/", "utf-8")
                    self.stream_sender_socket.sendto(header + payload, address)
        except Exception as err:
            print(str(err))
            self.send_audio_to_participants(payload)

    def send_video_to_participants(self, payload, frame_client_id):
        participants = self.meeting_session.participants
        try:
            for client_id, client_addresses in participants.items():
                if "-1" in client_addresses[3] or frame_client_id in client_addresses[3]:
                    address = client_addresses[0]
                    frame = payload[0]
                    timestamp = str(payload[1])
                    while len(timestamp) < 7:
                        timestamp = timestamp + "0"
                    image_chunks = functions.split_into_chunks(frame, self.UDP_payload_size)
                    chunk_order_number = 1
                    packet_count = math.ceil(len(frame) / self.UDP_payload_size)
                    for chunk in image_chunks:
                        header = bytes(str(timestamp) + "\\/" + str(chunk_order_number) + "\\/"
                                       + str(frame_client_id) + "\\/" + str(packet_count) + "\\/", "utf-8")
                        self.stream_sender_socket.sendto(header + chunk, address)
                        chunk_order_number += 1
        except:
            self.send_video_to_participants(payload, frame_client_id)

    def process_video_packets(self):
        while self.video_receiver_on:
            if not self.video_packet_queue.empty():
                try:
                    packet = self.video_packet_queue.get()
                    address = packet[1]
                    header = packet[0][:41].decode().split("\/")
                    timestamp = float(header[0])
                    packet_number = int(header[1])
                    client_id = (header[2], address[0], address[1])
                    packets_per_frame_ = int(header[3])
                    if client_id in self.video_data_frames:
                        frame_data = self.video_data_frames[client_id]
                        if packet_number == 1 and timestamp > frame_data[1]:
                            payload = b""
                            payload += packet[0][41:]
                            self.video_data_frames[client_id] = [payload, timestamp, packet_number]
                            if packet_number == packets_per_frame_:
                                self.send_video_to_participants(self.video_data_frames.pop(client_id), header[2])
                        elif packet_number == frame_data[2] + 1 and timestamp == frame_data[1]:
                            frame_data[0] += packet[0][41:]
                            frame_data[2] = packet_number
                            if packet_number == packets_per_frame_:
                                self.send_video_to_participants(frame_data, header[2])
                                del self.video_data_frames[client_id]
                            else:
                                self.video_data_frames[client_id] = frame_data
                        else:
                            del self.video_data_frames[client_id]
                    else:
                        if packet_number == 1:
                            payload = b""
                            payload += packet[0][41:]
                            self.video_data_frames[client_id] = [payload, timestamp, packet_number]
                            if packet_number == packets_per_frame_:
                                self.send_video_to_participants(self.video_data_frames.pop(client_id), header[2])
                except:
                    pass

    def process_audio_packets(self, packet):
        self.send_audio_to_participants(packet[0])

    def receive_video(self):
        while self.video_receiver_on:
            try:
                self.video_packet_queue.put(self.UDP_video_socket.recvfrom(self.UDP_packet_size))
            except:
                pass

    def receive_audio(self):
        while self.audio_receiver_on:
            try:
                self.process_audio_packets(self.UDP_audio_socket.recvfrom(self.UDP_packet_size))
            except:
                pass

    def stop_audio_receiver(self):
        self.audio_receiver_on = False

    def stop_video_receiver(self):
        self.video_receiver_on = False

    def start_audio_receiver(self):
        self.UDP_audio_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.UDP_audio_socket.bind((self.local_IP, 0))
        self.UDP_audio_socket.settimeout(5)
        self.audio_handler_thread = threading.Thread(target=self.receive_audio)
        self.audio_handler_thread.start()
        return self.UDP_audio_socket.getsockname()

    def start_video_receiver(self):
        self.UDP_video_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.UDP_video_socket.bind((self.local_IP, 0))
        self.UDP_video_socket.settimeout(5)
        self.video_handler_thread = threading.Thread(target=self.receive_video)
        self.video_packet_processor = threading.Thread(target=self.process_video_packets)
        self.video_handler_thread.start()
        self.video_packet_processor.start()
        return self.UDP_video_socket.getsockname()

    def start_stream_handler(self, session_socket):
        return self.start_video_receiver(), self.start_audio_receiver(), session_socket
