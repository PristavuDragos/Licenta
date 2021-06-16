import socket
import time
import feed_receiver
import main_client
import threading

received_response = None
receive_packets = None
connection_timeout = None
server_session_address = None
response_status = None


def packet_receiver(*args, **signals):
    global received_response
    global connection_timeout
    global receive_packets
    global server_session_address
    global response_status
    server_session_address = args[0]
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
            # if payload[0] == "Request Accepted":
            #     received_response = True
            # elif payload[0] == "Connection Accepted":
            #     received_response = True
            #     main_client.set_addresses([(payload[1], int(payload[2])), (payload[3], int(payload[4]))])
            #     server_session_address = (payload[5], int(payload[6]))
            #     signals["connected"].emit()
            if payload[0] == "ParticipantsList":
                main_client.set_participant_list(payload[1])
                signals["update_callback"].emit(main_client.participant_list)
                connection_timeout = time.perf_counter()
            elif payload[0] == "KeepAlive":
                connection_timeout = time.perf_counter()
            elif payload[0] == "CloseSession":
                signals["close_session"].emit()
            elif payload[0] == "TestTimer":
                print("dea")
                params = [int(payload[1]), int(payload[2]), int(payload[3])]
                signals["test_timer"].emit(params)
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
            if payload[0] == "CreateSession":
                received_response = True
                response_status = int(payload[1])
        except:
            pass
    if attempt_count == 2 and response_status == -1:
        return ["Server did not respond."]
    elif response_status == 0:
        return ["Creation failed."]
    else:
        session_code = payload[2]
        return ["Session created.", session_code]


def connect_to_session(params):
    global received_response
    global connection_timeout
    global response_status
    global server_session_address
    server_session_address = ()
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
            if payload[0] == "ConnectToSession":
                received_response = True
                main_client.set_addresses([(payload[1], int(payload[2])), (payload[3], int(payload[4]))])
                server_video_address = (payload[1], int(payload[2]))
                server_audio_address = (payload[3], int(payload[4]))
                server_session_address = (payload[5], int(payload[6]))
                session_owner = payload[7]
                response_status = 1
            elif payload[0] == "InvalidSession":
                response_status = 0
                received_response = True
        except Exception as err:
            print(str(err))
            pass
    if attempt_count == 2 and response_status == -1:
        feed_receiver.stop_audio_receiver()
        feed_receiver.stop_video_receiver()
        return ["Server did not respond."]
    elif response_status == 0:
        feed_receiver.stop_audio_receiver()
        feed_receiver.stop_video_receiver()
        return ["Invalid session credentials."]
    else:
        connection_timeout = time.perf_counter()
        return ["Connected.", server_session_address, server_video_address, server_audio_address, session_owner]


def close_session(session_code, client_id):
    global received_response
    global response_status
    receiver_socket = main_client.main_client_socket
    sock_address = receiver_socket.getsockname()
    sender_socket = main_client.sender_socket
    received_response = False
    response_status = -1
    message = bytes("CloseSession" + "\\/" + str(sock_address[0]) + "\\/" + str(sock_address[1]) + "\\/" +
                    session_code + "\\/" + client_id, "utf-8")
    sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))


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


def require_feeds(list_index):
    sender_socket = main_client.sender_socket
    message = bytes("RequireFeeds" + "\\/" + str(main_client.client_id) + "\\/" + str(list_index), "utf-8")
    sender_socket.sendto(message, server_session_address)


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


def upload_file(params):
    filename = params[0]
    session_code = params[1]
    file_type = params[2]
    try:
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client_socket.connect((main_client.settings["server_IP"], main_client.settings["server_TCP_PORT"]))
        tcp_client_socket.settimeout(5)
        print(filename)
        if file_type == 0:
            message = bytes("UploadTest" + "\\/" + session_code, "utf-8")
            tcp_client_socket.send(message)
        elif file_type == 1:
            username = params[3]
            message = bytes("UploadSolution" + "\\/" + session_code + "\\/" + username, "utf-8")
            tcp_client_socket.send(message)
        response = tcp_client_socket.recv(1024).decode()
        print(response)
        if response == "Start":
            file = open(filename, "rb")
            data = file.read(1024)
            while data:
                tcp_client_socket.send(data)
                data = file.read(1024)
            file.close()
            print("Done")
        tcp_client_socket.close()
    except Exception as err:
        print(err)
        return -1
    return 1


def download_subject(params):
    session_code = params[0]
    filename = params[1]
    try:
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client_socket.connect((main_client.settings["server_IP"], main_client.settings["server_TCP_PORT"]))
        tcp_client_socket.settimeout(5)
        message = bytes("DownloadSubject" + "\\/" + session_code, "utf-8")
        tcp_client_socket.send(message)
        response = tcp_client_socket.recv(1024).decode()
        print(response)
        checker = "Done".encode("utf-8")
        if response == "Proceed":
            file = open(filename, "wb")
            tcp_client_socket.send("Start".encode("utf-8"))
            while True:
                data = tcp_client_socket.recv(1024)
                print(data)
                if not data:
                    break
                else:
                    if checker in data:
                        file.write(data[:-4])
                        break
                    file.write(data)
            file.close()
        tcp_client_socket.close()
    except Exception as err:
        print(err)
        return -1
    return 1


def download_solutions(params):
    session_code = params[0]
    directory_name = params[1]
    finished = False
    try:
        tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_client_socket.connect((main_client.settings["server_IP"], main_client.settings["server_TCP_PORT"]))
        tcp_client_socket.settimeout(5)
        message = bytes("DownloadSolutions" + "\\/" + session_code, "utf-8")
        tcp_client_socket.send(message)
        response = tcp_client_socket.recv(1024).decode()
        done_bytes = "Done".encode("utf-8")
        end_bytes = "End".encode("utf-8")
        if response == "Proceed":
            while not finished:
                tcp_client_socket.send("Next".encode("utf-8"))
                username = tcp_client_socket.recv(1024).decode()
                if username == "End":
                    finished = True
                    break
                print(directory_name + "/" + username + ".pdf")
                file = open(directory_name + "/" + username + ".pdf", "wb")
                tcp_client_socket.send("Start".encode("utf-8"))
                while True:
                    data = tcp_client_socket.recv(1024)
                    if not data:
                        break
                    else:
                        if done_bytes in data and end_bytes not in data:
                            file.write(data[:-4])
                            break
                        elif done_bytes in data and end_bytes in data:
                            finished = True
                            file.write(data[:-7])
                            break
                        elif done_bytes not in data and end_bytes in data:
                            finished = True
                            break
                        file.write(data)
                file.close()
        tcp_client_socket.close()
    except Exception as err:
        print(err)
        return -1
    return 1


def start_test():
    global server_session_address
    sender_socket = main_client.sender_socket
    message = bytes("StartTest" + "\\/", "utf-8")
    sender_socket.sendto(message, server_session_address)


def close_connection():
    pass
