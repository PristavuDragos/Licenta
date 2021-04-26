import json
import threading
import socket

global settings


def init_settings():
    global settings
    with open("../Assets/global_settings.json", "r") as settings_file:
        settings = json.load(settings_file)




if __name__ == '__main__':
    pass
