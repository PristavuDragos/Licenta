import json
import threading
import socket
import audio_stream
import video_stream
import main_GUI

global settings


def init_settings():
    global settings
    with open("../Settings/global_settings.json", "r") as settings_file:
        settings = json.load(settings_file)


def start_client():
    connect_to_server()
    main_GUI.init_settings()
    main_GUI.start_ui()


def connect_to_server():
    audio_stream.init(settings)
    audio_stream.start_audio_feed()
    video_stream.init(settings)
    video_stream.start_video_feed()


def close():
    video_stream.stop_video_feed()
    audio_stream.stop_audio_feed()


if __name__ == '__main__':
    init_settings()
    start_client()
