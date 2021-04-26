import time
import socket
import cv2
import imutils
import threading

UDP_packet_size = None
server_PORT = None
server_IP = None
video_PORT = None
frame_width = None
frame_height = None
UDPClientSocket = None
feed_is_on = None


def split_into_chunks(bitstring, chunk_size):
    chunk_size = max(1, chunk_size)
    return (bitstring[i:i + chunk_size] for i in range(0, len(bitstring), chunk_size))


def init(settings):
    global UDP_packet_size
    global server_PORT
    global video_PORT
    global server_IP
    global UDPClientSocket
    global feed_is_on
    feed_is_on = False
    UDP_packet_size = settings["UDP_packet_size"]
    server_PORT = settings["server_PORT"]
    video_PORT = settings["video_PORT"]
    server_IP = settings["server_IP"]
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


def video_feed():
    capture = cv2.VideoCapture(0)
    initial_time = time.perf_counter()
    while feed_is_on:
        ret, frame = capture.read()
        frame = imutils.resize(frame, width=frame_width, height=frame_height)
        timestamp = str(time.perf_counter() - initial_time)[0:7]
        byteImage = frame.tobytes()
        image_chunks = split_into_chunks(byteImage, UDP_packet_size)
        chunk_order_number = 1
        for chunk in image_chunks:
            header = bytes(timestamp + "\\/" + str(chunk_order_number) + "\\/", "utf-8")
            UDPClientSocket.sendto(header + chunk, (server_IP, video_PORT))
            chunk_order_number += 1
        time.sleep(0.05)
        if cv2.waitKey(1) & 0xFF == ord('q') or not feed_is_on:
            break

    capture.release()
    cv2.destroyAllWindows()


def start_video_feed():
    global feed_is_on
    video_thread = threading.Thread(target=video_feed)
    feed_is_on = True
    video_thread.start()
    video_thread.join()


def stop_video_feed():
    global feed_is_on
    feed_is_on = False
