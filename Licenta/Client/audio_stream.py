import pyaudio
import time
import threading
import main_client
import wave

UDP_packet_size = None
UDP_payload_size = None
server_PORT = None
server_IP = None
audio_PORT = None
channels = None
fs = None
sample_format = None
sample_chunk_size = None
sender_socket = None
feed_is_on = None


def init(settings, address):
    global UDP_packet_size
    global UDP_payload_size
    global server_PORT
    global audio_PORT
    global server_IP
    global channels
    global fs
    global sample_format
    global sample_chunk_size
    global sender_socket
    global feed_is_on
    feed_is_on = False
    UDP_packet_size = settings["UDP_packet_size"]
    UDP_payload_size = settings["UDP_payload_size"]
    server_PORT = settings["server_PORT"]
    audio_PORT = address[1]
    server_IP = address[0]
    channels = settings["audio_channels"]
    fs = settings["audio_fs"]
    sample_chunk_size = settings["audio_sample_chunk_size"]
    sample_format = pyaudio.paInt16
    sender_socket = main_client.sender_socket


def audio_feed():
    #audio_test()
    initial_time = time.perf_counter()
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=sample_chunk_size,
                    input=True)
    while feed_is_on:
        payload = b""
        while len(payload) < 61440:
            data = stream.read(sample_chunk_size)
            payload += data
        timestamp = str(time.perf_counter() - initial_time)[0:7]
        header = bytes(timestamp + "\\/", "utf-8")
        sender_socket.sendto(header + payload, (server_IP, audio_PORT))

    stream.stop_stream()
    stream.close()
    p.terminate()


def audio_test():
    initial_time = time.perf_counter()
    p = pyaudio.PyAudio()
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=sample_chunk_size,
                    input=True)
    filename = "../Assets/WAV_files/applause.wav"
    af = wave.open(filename, 'rb')
    while feed_is_on:
        data = af.readframes(sample_chunk_size)
        if data == "":
            af = wave.open(filename, 'rb')
            data = af.readframes(sample_chunk_size)
        payload = b""
        while len(payload) < 61440:
            payload += data
            data = af.readframes(sample_chunk_size)
        timestamp = str(time.perf_counter() - initial_time)[0:7]
        header = bytes(timestamp + "\\/", "utf-8")
        sender_socket.sendto(header + payload, (server_IP, audio_PORT))
        time.sleep(0.3)

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
