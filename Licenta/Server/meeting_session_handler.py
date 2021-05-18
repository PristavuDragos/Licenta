import socket
import threading
import time

import stream_handler
import main_server

session_active = None
participants = None
participants_keep_alive = None
owner = None
session_socket = None
sender_socket = None


def init_session(session_owner, settings):
    global session_active
    global participants
    global owner
    global session_socket
    global participants_keep_alive
    global sender_socket
    session_active = True
    participants = {}
    participants_keep_alive = {}
    owner = session_owner
    session_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    session_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    session_socket.bind((settings["server_IP"], 0))
    session_socket.settimeout(5)
    sender_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


def connect_client(params):
    client_id = str(params[0])
    if client_id not in participants:
        participants[client_id] = [(params[1], int(params[2])), (params[3], int(params[4])),
                                   (params[5], int(params[6])), ["-1"]]
        send_participant_list()


def disconnect_client(client_id):
    global participants
    global participants_keep_alive
    participants.pop(client_id, None)
    participants_keep_alive.pop(client_id, None)
    send_participant_list()


def send_participant_list():
    participant_list = str(participants.keys())
    for client_id, client_addresses in participants.items():
        address = client_addresses[2]
        message = bytes("ParticipantsList" + "\\/" + participant_list + "\\/", "utf-8")
        sender_socket.sendto(message, address)


def check_session_still_active():
    global session_active
    if session_active:
        if len(participants) == 0 or True:
            session_active = True
        else:
            session_active = True


def run_session(session_id):
    global participants_keep_alive
    while session_active:
        try:
            packet = session_socket.recvfrom(main_server.settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            if payload[0] == "KeepAlive":
                participants_keep_alive[payload[1]] = time.perf_counter()
            elif payload[0] == "RequireFeeds":
                pass
        except:
            pass
        check_session_still_active()


def close_session(session_id):
    global session_active
    session_active = False
    stream_handler.stop_audio_receiver()
    stream_handler.stop_video_receiver()


def start_session(session_id, session_owner, settings):
    session_thread = threading.Thread(target=run_session, args=[session_id])
    init_session(session_owner, settings)
    session_thread.start()
    return stream_handler.start_stream_handler(settings, session_socket.getsockname())