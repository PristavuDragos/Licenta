import pyaudio
import time
import socket
import threading

UDP_packet_size = None
server_PORT = None
server_IP = None
audio_PORT = None
channels = None
fs = None
sample_format = None
sample_chunk_size = None
UDPClientSocket = None
feed_is_on = None


def init(settings):
    global UDP_packet_size
    global server_PORT
    global audio_PORT
    global server_IP
    global channels
    global fs
    global sample_format
    global sample_chunk_size
    global UDPClientSocket
    global feed_is_on
    feed_is_on = False
    UDP_packet_size = settings["UDP_packet_size"]
    server_PORT = settings["server_PORT"]
    audio_PORT = settings["audio_PORT"]
    server_IP = settings["server_IP"]
    channels = settings["audio_channels"]
    fs = settings["audio_fs"]
    sample_chunk_size = settings["audio_sample_chunk_size"]
    sample_format = pyaudio.paInt16
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)


def audio_feed():
    initial_time = time.perf_counter()
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=sample_chunk_size,
                    input=True)
    while feed_is_on:
        payload = b""
        while len(payload) < 20480:
            data = stream.read(sample_chunk_size)
            payload += data
        timestamp = str(time.perf_counter() - initial_time)[0:7]
        header = bytes(timestamp + "\\/", "utf-8")
        UDPClientSocket.sendto(header + payload, (server_IP, audio_PORT))

    stream.stop_stream()
    stream.close()
    p.terminate()


def start_audio_feed():
    global feed_is_on
    audio_thread = threading.Thread(target=audio_feed)
    feed_is_on = True
    audio_thread.start()
#    audio_thread.join()


def stop_audio_feed():
    global feed_is_on
    feed_is_on = False
