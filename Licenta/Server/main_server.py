import json
import meeting_session_handler
import threading
import socket

settings = None
keep_server_up = None
main_server_socket = None
server_sender_socket = None
existing_sessions = None


def init_settings():
    global settings
    with open("../Settings/global_settings.json", "r") as settings_file:
        settings = json.load(settings_file)


def run_server():
    while keep_server_up:
        try:
            packet = main_server_socket.recvfrom(settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            if payload[0] == "CreateSession":
                create_request(payload)
            elif payload[0] == "ConnectToSession":
                connect_request(payload)
        except:
            pass


def create_request(payload):
    try:
        address = (payload[2], int(payload[3]))
        start_meeting_session("Test", [payload[1], payload[2], payload[3]])
        message = bytes("Request Accepted" + "\\/", "utf-8")
        server_sender_socket.sendto(message, address)
    except BaseException as err:
        server_sender_socket.sendto(bytes(err), address)


def connect_request(payload):
    address = (payload[2], int(payload[3]))
    meeting_session_handler.connect_client([payload[1], payload[5], payload[6], payload[7],
                                            payload[8], payload[2], payload[3]])
    session_id = payload[4]
    if session_id in existing_sessions:
        session_addresses = existing_sessions[session_id]
        message = bytes("Connection Accepted" + "\\/" + str(session_addresses[0][0]) + "\\/"
                        + str(session_addresses[0][1]) + "\\/" + str(session_addresses[1][0])
                        + "\\/" + str(session_addresses[1][1]) + "\\/" + str(session_addresses[2][0])
                        + "\\/" + str(session_addresses[2][1]) + "\\/", "utf-8")
        server_sender_socket.sendto(message, address)
    else:
        server_sender_socket.sendto(bytes("Invalid meeting", "utf-8"), address)


def server_stopping():
    global keep_server_up
    while keep_server_up:
        input_string = input("Q/Quit/q/quit to stop server:\n")
        if input_string in ["q", "Q", "quit", "Quit"]:
            keep_server_up = False
            meeting_session_handler.close_session("Test")


def start_meeting_session(session_id, owner):
    global existing_sessions
    if session_id not in existing_sessions:
        existing_sessions[session_id] = meeting_session_handler.start_session(session_id, owner, settings)


def start_server():
    global keep_server_up
    global main_server_socket
    global server_sender_socket
    global existing_sessions
    init_settings()
    try:
        main_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        main_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        main_server_socket.bind((settings["server_IP"], settings["server_PORT"]))
        main_server_socket.settimeout(5)
        server_sender_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    except BaseException as err:
        print("An error occurred while starting the server: " + str(err))
    else:
        print("Server is running.")
    existing_sessions = {}
    keep_server_up = True
    stopper_thread = threading.Thread(target=server_stopping)
    stopper_thread.start()
    run_server()


if __name__ == '__main__':
    start_server()
