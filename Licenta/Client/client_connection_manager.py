import time
import feed_receiver
import main_client
import threading

received_response = None
receive_packets = None
connection_timeout = None
server_session_address = None
response_status = None


def packet_receiver(**signals):
    global received_response
    global connection_timeout
    global receive_packets
    global server_session_address
    global response_status
    receive_packets = True
    connection_timeout = time.perf_counter()
    socket = main_client.main_client_socket
    last_ka_packet_sent = time.perf_counter()
    while receive_packets:
        try:
            timestamp = time.perf_counter()
            if timestamp - last_ka_packet_sent > 4:
                last_ka_packet_sent = timestamp
                keep_connection_alive()
            packet = socket.recvfrom(main_client.settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            if payload[0] != "KeepAlive":
                print(payload)
            if payload[0] == "Request Accepted":
                received_response = True
            elif payload[0] == "Connection Accepted":
                received_response = True
                main_client.set_addresses([(payload[1], int(payload[2])), (payload[3], int(payload[4]))])
                server_session_address = (payload[5], int(payload[6]))
                signals["connected"].emit()
            elif payload[0] == "ParticipantsList":
                main_client.set_participant_list(payload[1])
                signals["update_callback"].emit(main_client.participant_list)
                connection_timeout = time.perf_counter()
            elif payload[0] == "KeepAlive":
                connection_timeout = time.perf_counter()
        except:
            if time.perf_counter() - connection_timeout > main_client.settings["connection_timeout"]:
                main_client.close()
                receive_packets = False
                pass


def set_received_response(boolean):
    global received_response
    received_response = boolean


def set_response_status(status):
    global response_status
    response_status = status


def initiate_session(params):
    global received_response
    global response_status
    receiver_socket = main_client.main_client_socket
    sock_address = receiver_socket.getsockname()
    sender_socket = main_client.sender_socket
    received_response = False
    response_status = -1
    attempt_count = 0
    payload = None
    message = bytes("CreateSession" + "\\/" + str(main_client.client_id) + "\\/" +
                    str(sock_address[0]) + "\\/" + str(sock_address[1]) + "\\/" + params[0] +
                    "\\/" + params[1] + "\\/" + params[2] + "\\/" + params[3] + "\\/", "utf-8")
    while not received_response and attempt_count < 2:
        attempt_count += 1
        sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))
        try:
            packet = receiver_socket.recvfrom(main_client.settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            print(payload)
            if payload[0] == "CreateSession":
                received_response = True
                response_status = int(payload[1])
        except:
            pass
    if attempt_count == 2:
        return "Server did not respond."
    elif response_status == 0:
        return "Creation failed."
    else:
        session_code = payload[2]
        return "Session created.\n Code: " + str(session_code)


def connect_to_session(params):
    global received_response
    global connection_timeout
    global response_status
    global server_session_address
    main_client.settings
    video_sock, audio_sock = feed_receiver.start_feed_receiver(main_client.settings)
    receiver_socket = main_client.main_client_socket
    sock_address = receiver_socket.getsockname()
    sender_socket = main_client.sender_socket
    received_response = False
    response_status = -1
    attempt_count = 0
    payload = None
    session_code = params[0]
    password = params[1]
    message = bytes("ConnectToSession" + "\\/" + str(main_client.client_id) + "\\/" + str(sock_address[0]) +
                    "\\/" + str(sock_address[1]) + "\\/" +str(session_code) + "\\/" + str(video_sock[0]) +
                    "\\/" + str(video_sock[1]) + "\\/" + str(audio_sock[0]) + "\\/" + str(audio_sock[1]) +
                    "\\/" + password + "\\/" + main_client.client_name, "utf-8")
    while not received_response and attempt_count < 2:
        attempt_count += 1
        sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))
        try:
            packet = receiver_socket.recvfrom(main_client.settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            print(payload)
            if payload[0] == "ConnectToSession":
                received_response = True
                main_client.set_addresses([(payload[1], int(payload[2])), (payload[3], int(payload[4]))])
                server_session_address = (payload[5], int(payload[6]))
                response_status = 1
            elif payload[0] == "InvalidSession":
                response_status = 0
                received_response = True
        except:
            pass
    if attempt_count == 2:
        feed_receiver.stop_audio_receiver()
        feed_receiver.stop_video_receiver()
        return "Server did not respond."
    elif response_status == 0:
        feed_receiver.stop_audio_receiver()
        feed_receiver.stop_video_receiver()
        return "Invalid session credentials."
    else:
        connection_timeout = time.perf_counter()
        main_client.start_stream()
        return "Connected."


def disconnect_from_session():
    global server_session_address
    global receive_packets
    if receive_packets:
        sender_socket = main_client.sender_socket
        message = bytes("Disconnect" + "\\/" + str(main_client.client_id) + "\\/", "utf-8")
        sender_socket.sendto(message, server_session_address)


def keep_connection_alive():
    global server_session_address
    sender_socket = main_client.sender_socket
    message = bytes("KeepAlive" + "\\/" + str(main_client.client_id) + "\\/", "utf-8")
    sender_socket.sendto(message, server_session_address)


def require_feeds(client_ids):
    sender_socket = main_client.sender_socket
    message = bytes("RequireFeeds" + "\\/" + str(main_client.client_id) + "\\/", "utf-8")
    sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))


def stop_packet_receiver():
    global receive_packets
    receive_packets = False


def register_request(params):
    global received_response
    global response_status
    mail = params[0]
    username = params[1]
    password = params[2]
    receiver_socket = main_client.main_client_socket
    sock_address = receiver_socket.getsockname()
    sender_socket = main_client.sender_socket
    received_response = False
    response_status = -1
    attempt_count = 0
    message = bytes("Register" + "\\/" + str(sock_address[0]) + "\\/" + str(sock_address[1]) + "\\/" +
                    mail + "\\/" + username + "\\/" + password + "\\/", "utf-8")
    while not received_response and attempt_count < 2:
        attempt_count += 1
        sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))
        try:
            packet = receiver_socket.recvfrom(main_client.settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            if payload[0] == "Register":
                received_response = True
                response_status = int(payload[1])
        except:
            pass
    if attempt_count == 2:
        return "Server did not respond!"
    elif response_status == 0:
        return "Email already in use!"
    else:
        return "Account created!"


def login_request(params):
    global received_response
    global response_status
    email = params[0]
    password = params[1]
    receiver_socket = main_client.main_client_socket
    sock_address = receiver_socket.getsockname()
    sender_socket = main_client.sender_socket
    received_response = False
    response_status = -1
    attempt_count = 0
    payload = None
    message = bytes("Login" + "\\/" + str(sock_address[0]) + "\\/" + str(sock_address[1]) + "\\/" +
                    email + "\\/" + password + "\\/", "utf-8")
    while not received_response and attempt_count < 2:
        attempt_count += 1
        sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))
        try:
            packet = receiver_socket.recvfrom(main_client.settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            if payload[0] == "Login":
                received_response = True
                response_status = int(payload[1])
        except:
            pass
    if attempt_count == 2:
        return "Server did not respond!"
    elif response_status == 0:
        return "Login failed!"
    elif response_status == 1:
        return "Invalid username or password!"
    elif response_status == 2:
        main_client.set_client(payload[2], payload[3])
        main_client.change_login_status(1)
        return "Logged in successfully!"


def close_connection():
    pass
