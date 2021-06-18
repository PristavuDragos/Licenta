import socket
import threading
import time
import stream_handler
import main_server


class MeetingSession:
    def __init__(self, session_owner, session_id, times, settings):
        self.settings = settings
        self.session_thread = threading.Thread(target=self.run_session, args=[session_id, settings])
        self.session_active = True
        self.participants = {}
        self.waiting_room = {}
        self.participants_keep_alive = {}
        self.owner = session_owner
        self.test_start_timestamp = -1
        self.test_duration = times[0]
        self.test_upload_time = times[1]
        self.session_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.session_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.session_socket.bind((settings["server_IP"], 0))
        self.session_socket.settimeout(5)
        self.sender_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.stream_handler = stream_handler.StreamHandler(settings, self)

    def connect_client(self, params):
        client_id = str(params[0])
        if client_id not in self.participants:
            self.participants[client_id] = [(params[1], int(params[2])), (params[3], int(params[4])),
                                            (params[5], int(params[6])), ["-1"], params[7]]
            self.send_participant_list()
            if self.test_start_timestamp != -1:
                elapsed_time = round(time.perf_counter() - self.test_start_timestamp) // 60
                self.send_test_timer(client_id, elapsed_time)

    def put_client_in_waiting_room(self, params):
        client_id = str(params[0])
        if client_id == self.owner[0]:
            message = bytes("ApprovalMessage" + "\\/" + "1", "utf-8")
            self.sender_socket.sendto(message, (self.owner[1], int(self.owner[2])))
        elif client_id not in self.waiting_room:
            self.waiting_room[client_id] = [params[1], params[2]]
            self.send_waiting_list()

    def send_waiting_list(self):
        waiting_list = []
        for key, value in self.waiting_room.items():
            waiting_list.append([key, value[0]])
        message = bytes("WaitingList" + "\\/" + str(waiting_list), "utf-8")
        self.sender_socket.sendto(message, (self.owner[1], int(self.owner[2])))

    def send_approval_messages(self, approval_list):
        for it in approval_list:
            if it[0] in self.waiting_room:
                try:
                    values = self.waiting_room.pop(it[0], None)
                    message = bytes("ApprovalMessage" + "\\/" + it[1], "utf-8")
                    self.sender_socket.sendto(message, values[1])
                except Exception as err:
                    print(err)
        self.send_waiting_list()

    def disconnect_client(self, client_id):
        self.participants.pop(client_id, None)
        self.participants_keep_alive.pop(client_id, None)
        self.waiting_room.pop(client_id, None)
        self.send_participant_list()

    def send_participant_list(self):
        participant_list = []
        for key, value in self.participants.items():
            participant_list.append([key, value[4]])
        for client_id, client_addresses in self.participants.items():
            address = client_addresses[2]
            message = bytes("ParticipantsList" + "\\/" + str(participant_list) + "\\/", "utf-8")
            self.sender_socket.sendto(message, address)

    def send_disconnect_message(self):
        for client_id, client_addresses in self.participants.items():
            address = client_addresses[2]
            message = bytes("CloseSession" + "\\/", "utf-8")
            self.sender_socket.sendto(message, address)

    def send_keep_alive_packet(self, client_id):
        if client_id in self.participants:
            address = self.participants.get(client_id)[2]
            message = bytes("KeepAlive" + "\\/", "utf-8")
            self.sender_socket.sendto(message, address)

    def check_session_still_active(self):
        if self.session_active:
            if len(self.participants) == 0 or True:
                self.session_active = True
            else:
                self.session_active = True

    def send_initial_timer(self):
        for client_id in self.participants.keys():
            self.send_test_timer(client_id, 0)

    def send_test_timer(self, client_id, elapsed_time):
        address = self.participants.get(client_id)[2]
        message = bytes("TestTimer" + "\\/" + str(elapsed_time) + "\\/" + str(self.test_duration)
                        + "\\/" + str(self.test_upload_time), "utf-8")
        self.sender_socket.sendto(message, address)

    def run_session(self, session_id, settings):
        timer = time.perf_counter()
        timeout = self.settings["connection_timeout"]
        while self.session_active:
            try:
                packet = self.session_socket.recvfrom(settings["UDP_packet_size"])
                payload = packet[0].decode().split("\/")
                if payload[0] == "KeepAlive":
                    self.participants_keep_alive[payload[1]] = time.perf_counter()
                    self.send_keep_alive_packet(payload[1])
                elif payload[0] == "RequireFeeds":
                    index = int(payload[2])
                    if index < 15:
                        self.participants[payload[1]][3] = ["-1"]
                    else:
                        self.participants[payload[1]][3] = list(self.participants.keys())[index - 15:index]
                elif payload[0] == "Disconnect":
                    self.disconnect_client(payload[1])
                elif payload[0] == "StartTest":
                    self.test_start_timestamp = time.perf_counter()
                    self.send_initial_timer()
                elif payload[0] == "ApprovalList":
                    self.send_approval_messages(get_list_from_string(payload[1]))
            except Exception as err:
                pass
            current_time = time.perf_counter()
            if current_time - timer > 10:
                timer = current_time
                clients_to_dc = []
                for client_id, timestamp in self.participants_keep_alive.items():
                    if current_time - timestamp > timeout:
                        clients_to_dc.append(client_id)
                for client_id in clients_to_dc:
                    self.disconnect_client(client_id)
            self.check_session_still_active()

    def close_session(self):
        self.session_active = False
        stream_handler.stop_audio_receiver()
        stream_handler.stop_video_receiver()

    # def start_session(self, settings):
    #     self.session_active = True
    #     self.session_thread.start()
    #     return stream_handler.start_stream_handler(settings, self.session_socket.getsockname())

    def start_session(self, session_id, settings):
        self.session_active = True
        self.session_thread = threading.Thread(target=self.run_session, args=[session_id, settings])
        self.session_thread.start()
        return self.stream_handler.start_stream_handler(self.session_socket.getsockname())


def get_list_from_string(string_list):
    list_ = []
    try:
        string_list = string_list.split("\'")
        iterator = 0
        while iterator < len(string_list):
            if iterator % 2 == 1:
                list_.append([string_list[iterator], string_list[iterator + 2]])
                iterator += 2
            iterator += 1
        return list_
    except Exception as err:
        print(err)


# def init_session(session_owner, settings):
#     global session_active
#     global participants
#     global owner
#     global session_socket
#     global participants_keep_alive
#     global sender_socket
#     session_active = True
#     participants = {}
#     participants_keep_alive = {}
#     owner = session_owner
#     session_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#     session_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     session_socket.bind((settings["server_IP"], 0))
#     session_socket.settimeout(5)
#     sender_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
#
#
# def connect_client(params):
#     client_id = str(params[0])
#     if client_id not in participants:
#         participants[client_id] = [(params[1], int(params[2])), (params[3], int(params[4])),
#                                    (params[5], int(params[6])), ["-1"]]
#         send_participant_list()
#
#
# def disconnect_client(client_id):
#     global participants
#     global participants_keep_alive
#     participants.pop(client_id, None)
#     participants_keep_alive.pop(client_id, None)
#     send_participant_list()
#
#
# def send_participant_list():
#     participant_list = str(participants.keys())
#     for client_id, client_addresses in participants.items():
#         address = client_addresses[2]
#         message = bytes("ParticipantsList" + "\\/" + participant_list + "\\/", "utf-8")
#         sender_socket.sendto(message, address)
#
#
# def send_keep_alive_packet(client_id):
#     if client_id in participants:
#         address = participants.get(client_id)[2]
#         message = bytes("KeepAlive" + "\\/", "utf-8")
#         sender_socket.sendto(message, address)
#
#
# def check_session_still_active():
#     global session_active
#     if session_active:
#         if len(participants) == 0 or True:
#             session_active = True
#         else:
#             session_active = True
#
#
# def run_session(session_id, settings):
#     global participants_keep_alive
#     timer = time.perf_counter()
#     while session_active:
#         try:
#             packet = session_socket.recvfrom(settings["UDP_packet_size"])
#             payload = packet[0].decode().split("\/")
#             if payload[0] == "KeepAlive":
#                 participants_keep_alive[payload[1]] = time.perf_counter()
#                 send_keep_alive_packet(payload[1])
#             elif payload[0] == "RequireFeeds":
#                 pass
#             elif payload[0] == "Disconnect":
#                 disconnect_client(payload[1])
#         except Exception as err:
#             pass
#         current_time = time.perf_counter()
#         if current_time - timer > 10:
#             timer = current_time
#             clients_to_dc = []
#             for client_id, timestamp in participants_keep_alive.items():
#                 if current_time - timestamp > settings["connection_timeout"]:
#                     clients_to_dc.append(client_id)
#             for client_id in clients_to_dc:
#                 disconnect_client(client_id)
#         check_session_still_active()
#
#
# def close_session(session_id):
#     global session_active
#     session_active = False
#     stream_handler.stop_audio_receiver()
#     stream_handler.stop_video_receiver()


# def start_session(session_id, session_owner, settings):
#     global session_active
#     session_active = True
#     session_thread = threading.Thread(target=run_session, args=[session_id, settings])
#     init_session(session_owner, settings)
#     session_thread.start()
#     return stream_handler.start_stream_handler(settings, session_socket.getsockname())
