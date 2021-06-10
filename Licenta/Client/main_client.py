import json
import random
import socket
import audio_stream
import video_stream
from Client import main_GUI
import client_connection_manager
import feed_receiver

client_settings = None
settings = None
main_client_socket = None
sender_socket = None
client_id = None
server_stream_addresses = None
main_window = None
participant_list = None
client_name = None


def init_settings():
    global settings
    global main_client_socket
    global sender_socket
    global client_settings
    global client_name
    with open("client_settings.json", "r") as settings_file:
        client_settings = json.load(settings_file)
    with open("../Settings/global_settings.json", "r") as settings_file:
        settings = json.load(settings_file)
    client_name = client_settings["username"]
    temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_socket.connect(('8.8.8.8', 1))
    settings["local_ip"] = temp_socket.getsockname()[0]
    del temp_socket
    main_client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    main_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    main_client_socket.bind((settings["local_ip"], 0))
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
    print(string_list)
    string_list = string_list.split("\'")
    iterator = 0
    while iterator < len(string_list):
        if iterator % 2 == 1:
            participant_list.append([string_list[iterator], string_list[iterator + 2]])
            iterator += 2
        iterator += 1


def set_addresses(addresses):
    global server_stream_addresses
    server_stream_addresses = addresses


def get_client_id():
    global client_settings
    global client_id
    client_id = client_settings["client_id"]


def set_client(new_id, username):
    global client_id
    global client_settings
    global client_name
    client_id = new_id
    client_settings["client_id"] = client_id
    client_name = username
    client_settings["username"] = username
    with open("client_settings.json", "w") as settings_file:
        json.dump(client_settings, settings_file)


def change_login_status(status):
    global client_settings
    client_settings["logged_in"] = status
    with open("client_settings.json", "w") as settings_file:
        json.dump(client_settings, settings_file)


def logout():
    global client_settings
    with open("client_settings.json", "r") as settings_file:
        client_settings = json.load(settings_file)
    set_client("-1", "")
    change_login_status(0)


def start_client():
    main_GUI.init_settings()
    main_GUI.start_ui()


def start_stream():
    video_stream.init(settings, server_stream_addresses[0])
    video_stream.start_video_feed_test()
    audio_stream.init(settings, server_stream_addresses[1])
    audio_stream.start_audio_feed()


# def connect_to_server(session_id):
#     if client_connection_manager.initiate_session():
#         if client_connection_manager.connect_to_session(session_id, settings):
#             audio_stream.init(settings, server_stream_addresses[1])
#             audio_stream.start_audio_feed()
#             video_stream.init(settings, server_stream_addresses[0])
#             video_stream.start_video_feed()


# def connect_to_server_test(session_id):
#     if client_connection_manager.connect_to_session(session_id, settings):
#         audio_stream.init(settings, server_stream_addresses[1])
#         audio_stream.start_audio_feed()
#         video_stream.init(settings, server_stream_addresses[0])
#         video_stream.start_video_feed_test()


def close():
    client_connection_manager.disconnect_from_session()
    video_stream.stop_video_feed()
    audio_stream.stop_audio_feed()
    feed_receiver.stop_audio_receiver()
    feed_receiver.stop_video_receiver()


if __name__ == '__main__':
    list = []
    for it in range(3):
        list.append(["dada", str(it)])
    print(str(list))
    start_client()
