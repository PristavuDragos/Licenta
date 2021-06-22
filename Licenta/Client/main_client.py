import json
import socket
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
    with open("../Settings/client_settings.json", "r") as settings_file:
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
    participant_list = get_list_from_string(string_list)


def get_list_from_string(string_list):
    list_ = []
    string_list = string_list.split("\'")
    iterator = 0
    while iterator < len(string_list):
        if iterator % 2 == 1:
            list_.append([string_list[iterator], string_list[iterator + 2]])
            iterator += 2
        iterator += 1
    return list_


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
    with open("../Settings/client_settings.json", "w") as settings_file:
        json.dump(client_settings, settings_file)


def change_login_status(status):
    global client_settings
    client_settings["logged_in"] = status
    with open("../Settings/client_settings.json", "w") as settings_file:
        json.dump(client_settings, settings_file)


def logout():
    global client_settings
    with open("../Settings/client_settings.json", "r") as settings_file:
        client_settings = json.load(settings_file)
    set_client("-1", "")
    change_login_status(0)


def start_client():
    main_GUI.init_settings()
    main_GUI.start_ui()


def close():
    client_connection_manager.disconnect_from_session()
    feed_receiver.stop_audio_receiver()
    feed_receiver.stop_video_receiver()
    client_connection_manager.stop_packet_receiver()


if __name__ == '__main__':
    start_client()
