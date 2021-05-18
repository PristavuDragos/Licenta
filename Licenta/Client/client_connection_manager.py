import time
import feed_receiver
import main_client
import threading

received_response = None
receive_packets = None
connection_timeout = None


def packet_receiver():
    global received_response
    global connection_timeout
    global receive_packets
    connection_timeout = time.perf_counter()
    socket = main_client.main_client_socket
    last_ka_packet_sent = time.perf_counter()
    while receive_packets:
        try:
            packet = socket.recvfrom(main_client.settings["UDP_packet_size"])
            payload = packet[0].decode().split("\/")
            print(payload)
            if payload[0] == "Request Accepted":
                received_response = True
            elif payload[0] == "Connection Accepted":
                received_response = True
                main_client.set_addresses([(payload[1], int(payload[2])), (payload[3], int(payload[4]))])
            elif payload[0] == "ParticipantsList":
                main_client.set_participant_list(payload[1])
                connection_timeout = time.perf_counter()
        except:
            if time.perf_counter() - last_ka_packet_sent > 14:
                keep_connection_alive()
            if time.perf_counter() - connection_timeout > 149:
                #disconnect
                receive_packets = False


def initiate_session():
    global received_response
    global receive_packets
    sock_address = main_client.main_client_socket.getsockname()
    sender_socket = main_client.sender_socket
    received_response = False
    response_catcher = threading.Thread(target=packet_receiver)
    receive_packets = True
    response_catcher.start()
    attempt_count = 0
    message = bytes("CreateSession" + "\\/" + str(main_client.client_id) + "\\/" +
                    str(sock_address[0]) + "\\/" + str(sock_address[1]), "utf-8")
    while not received_response and attempt_count < 10:
        attempt_count += 1
        sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))
        time.sleep(0.25)
    receive_packets = False
    response_catcher.join()
    if attempt_count == 10:
        print("Creation failed.")
        return False
    else:
        print("Session created")
        return True


def connect_to_session(params, settings):
    global received_response
    global receive_packets
    global connection_timeout
    video_sock, audio_sock = feed_receiver.start_feed_receiver(settings)
    sock_address = main_client.main_client_socket.getsockname()
    sender_socket = main_client.sender_socket
    received_response = False
    response_catcher = threading.Thread(target=packet_receiver)
    receive_packets = True
    response_catcher.start()
    attempt_count = 0
    session_id = params
    message = bytes("ConnectToSession" + "\\/" + str(main_client.client_id) + "\\/" +
                    str(sock_address[0]) + "\\/" + str(sock_address[1]) + "\\/" +
                    str(session_id) + "\\/" + str(video_sock[0]) + "\\/" + str(video_sock[1]) + "\\/" +
                    str(audio_sock[0]) + "\\/" + str(audio_sock[1]) + "\\/", "utf-8")
    while not received_response and attempt_count < 10:
        attempt_count += 1
        sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))
        time.sleep(0.25)
    if attempt_count == 10:
        print("Connection failed.")
        feed_receiver.stop_audio_receiver()
        feed_receiver.stop_video_receiver()
        stop_packet_receiver()
        return False
    else:
        print("Connected.")
        connection_timeout = time.perf_counter()
        return True


def keep_connection_alive():
    sender_socket = main_client.sender_socket
    message = bytes("KeepAlive" + "\\/" + str(main_client.client_id) + "\\/", "utf-8")
    sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))


def require_feeds(client_ids):
    sender_socket = main_client.sender_socket
    message = bytes("RequireFeeds" + "\\/" + str(main_client.client_id) + "\\/", "utf-8")
    sender_socket.sendto(message, (main_client.settings["server_IP"], main_client.settings["server_PORT"]))


def stop_packet_receiver():
    global receive_packets
    receive_packets = False


def close_connection():
    pass
