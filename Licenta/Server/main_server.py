import json
import meeting_session_handler
import threading
import socket
from Server.Database import user_collection, meeting_session_collection
from Server.Database import db_connection
from Server.file_serving_thread import FileServerThread
import Server.Database.meeting_session_collection as msc

settings = None
keep_server_up = None
main_server_socket = None
tcp_file_socket = None
server_sender_socket = None
existing_sessions_addresses = None
existing_sessions = None


def init_settings():
    global settings
    with open("../Settings/global_settings.json", "r") as settings_file:
        settings = json.load(settings_file)


def run_server():
    db_connection.init(settings)
    while keep_server_up:
        try:
            packet = main_server_socket.recvfrom(settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            if payload[0] == "CreateSession":
                create_request(payload)
            elif payload[0] == "ConnectToWaitingRoom":
                connect_to_waiting_room_request(payload)
            elif payload[0] == "ConnectToSession":
                connect_request(payload)
            elif payload[0] == "CloseSession":
                close_request(payload)
            elif payload[0] == "Register":
                register_request(payload)
            elif payload[0] == "Login":
                login_request(payload)
        except:
            pass


def file_manager():
    global tcp_file_socket
    threads = []
    while keep_server_up:
        tcp_file_socket.listen(10)
        (conn, (ip, port)) = tcp_file_socket.accept()
        handler = FileServerThread(ip, port, conn)
        handler.start()
        threads.append(handler)
    for t in threads:
        t.join()


def create_request(payload):
    try:
        address = (payload[2], int(payload[3]))
        session_id = msc.create_session([payload[4], payload[5], payload[1], payload[6], payload[7]])
        message = None
        if session_id is not None:
            start_meeting_session(session_id, [payload[1], payload[2], payload[3]], [payload[6], payload[7]])
            message = bytes("CreateSession" + "\\/" + "1" + "\\/" + session_id, "utf-8")
        else:
            message = bytes("CreateSession" + "\\/" + "0" + "\\/", "utf-8")
        server_sender_socket.sendto(message, address)
    except BaseException as err:
        server_sender_socket.sendto(bytes(err), address)


def connect_to_waiting_room_request(payload):
    address = (payload[2], int(payload[3]))
    session_code = payload[4]
    password = payload[5]
    validation = meeting_session_collection.validate_connection([session_code, password])
    if validation[0] and session_code in existing_sessions_addresses:
        message = bytes("ConnectToWaitingRoom" + "\\/", "utf-8")
        server_sender_socket.sendto(message, address)
        existing_sessions.get(session_code).put_client_in_waiting_room([payload[1], payload[6], address])
    else:
        server_sender_socket.sendto(bytes("InvalidSession", "utf-8"), address)


def connect_request(payload):
    address = (payload[2], int(payload[3]))
    session_code = payload[4]
    password = payload[9]
    validation = meeting_session_collection.validate_connection([session_code, password])
    if validation[0] and session_code in existing_sessions_addresses:
        session_addresses = existing_sessions_addresses[session_code]
        message = bytes("ConnectToSession" + "\\/" + str(session_addresses[0][0]) + "\\/"
                        + str(session_addresses[0][1]) + "\\/" + str(session_addresses[1][0])
                        + "\\/" + str(session_addresses[1][1]) + "\\/" + str(session_addresses[2][0])
                        + "\\/" + str(session_addresses[2][1]) + "\\/" + str(validation[1]), "utf-8")
        server_sender_socket.sendto(message, address)
        existing_sessions.get(session_code).connect_client([payload[1], payload[5], payload[6], payload[7],
                                                            payload[8], payload[2], payload[3], payload[10]])
    else:
        server_sender_socket.sendto(bytes("InvalidSession", "utf-8"), address)


def close_request(payload):
    session_code = payload[3]
    client_id = payload[4]
    if session_code in existing_sessions:
        session = existing_sessions.get(session_code)
        if session.owner[0] == client_id:
            session.send_disconnect_message()
            existing_sessions.pop(session_code)
            existing_sessions_addresses.pop(session_code)


def register_request(payload):
    address = (payload[1], int(payload[2]))
    result = user_collection.create_user([payload[4], payload[5], payload[3]])
    status = "0"
    if result is not None:
        status = "1"
    message = bytes("Register" + "\\/" + status + "\\/", "utf-8")
    server_sender_socket.sendto(message, address)


def login_request(payload):
    address = (payload[1], int(payload[2]))
    result = user_collection.check_credentials([payload[3], payload[4]])
    status = "2"
    if result is None:
        status = "0"
    elif result[0] == -1:
        status = "1"
    message = bytes("Login" + "\\/" + status + "\\/" + str(result[0]) + "\\/" + str(result[1]) + "\\/", "utf-8")
    server_sender_socket.sendto(message, address)


def server_stopping():
    global keep_server_up
    global existing_sessions
    while keep_server_up:
        input_string = input("Q/Quit/q/quit to stop server:\n")
        if input_string in ["q", "Q", "quit", "Quit"]:
            keep_server_up = False
            for session_id in existing_sessions.keys():
                existing_sessions.pop(session_id).close_session()


def start_meeting_session(session_id, owner, times):
    global existing_sessions_addresses
    global existing_sessions
    if session_id not in existing_sessions_addresses:
        session = meeting_session_handler.MeetingSession(owner, session_id, times, settings)
        existing_sessions[session_id] = session
        existing_sessions_addresses[session_id] = session.start_session(session_id, settings)


def start_server():
    global keep_server_up
    global main_server_socket
    global server_sender_socket
    global existing_sessions_addresses
    global existing_sessions
    global tcp_file_socket
    init_settings()
    try:
        main_server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        main_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        main_server_socket.bind((settings["server_IP"], settings["server_PORT"]))
        main_server_socket.settimeout(5)
        tcp_file_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        tcp_file_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        tcp_file_socket.bind((settings["server_IP"], settings["server_TCP_PORT"]))
        server_sender_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    except BaseException as err:
        print("An error occurred while starting the server: " + str(err))
    else:
        print("Server is running.")
    existing_sessions_addresses = {}
    existing_sessions = {}
    keep_server_up = True
    stopper_thread = threading.Thread(target=server_stopping)
    stopper_thread.start()
    file_thread = threading.Thread(target=file_manager)
    file_thread.start()
    run_server()


if __name__ == '__main__':
    start_server()
