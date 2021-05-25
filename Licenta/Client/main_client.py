import json
import random
import threading
import socket
import audio_stream
import video_stream
import main_GUI
import client_connection_manager
import feed_receiver

settings = None
main_client_socket = None
sender_socket = None
client_id = None
server_stream_addresses = None
main_window = None
participant_list = None


def init_settings():
    global settings
    global main_client_socket
    global sender_socket
    with open("../Settings/global_settings.json", "r") as settings_file:
        settings = json.load(settings_file)
    main_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    main_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    main_client_socket.bind((settings["server_IP"], 0))
    main_client_socket.settimeout(5)
    sender_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    get_client_id()


def set_window(window):
    global main_window
    main_window = window


def set_participant_list(string_list):
    global participant_list
    global main_window
    participant_list = []
    string_list = string_list.split("\'")
    for iterator in range(len(string_list)):
        if iterator % 2 == 1:
            participant_list.append(string_list[iterator])


def set_addresses(addresses):
    global server_stream_addresses
    server_stream_addresses = addresses


def get_client_id():
    global client_id
    temp = str(random.randrange(999999))
    while len(temp) < 6:
        temp = "0" + temp
    client_id = temp


def start_client():
    main_GUI.init_settings()
    main_GUI.start_ui()


def connect_to_server():
    if client_connection_manager.initiate_session():
        if client_connection_manager.connect_to_session("Test", settings):
            audio_stream.init(settings, server_stream_addresses[1])
            audio_stream.start_audio_feed()
            video_stream.init(settings, server_stream_addresses[0])
            video_stream.start_video_feed()


def connect_to_server_test():
    if client_connection_manager.connect_to_session("Test", settings):
        audio_stream.init(settings, server_stream_addresses[1])
        audio_stream.start_audio_feed()
        video_stream.init(settings, server_stream_addresses[0])
        video_stream.start_video_feed_test()


def close():
    client_connection_manager.disconnect_from_session()
    video_stream.stop_video_feed()
    audio_stream.stop_audio_feed()
    feed_receiver.stop_audio_receiver()
    feed_receiver.stop_video_receiver()
    client_connection_manager.stop_packet_receiver()


if __name__ == '__main__':
    start_client()
