import pyaudio
from Utils import functions
import main_client
import pygame

channels = None
fs = None
sample_chunk_size = None
sample_format = None
pa = None
stream_list = None
stream_cycle = None


def init():
    global channels
    global fs
    global sample_chunk_size
    global sample_format
    global pa
    global stream_list
    global stream_cycle
    pygame.init()
    pygame.mixer.init()
    stream_cycle = 0
    channels = main_client.settings["audio_channels"]
    fs = main_client.settings["audio_fs"]
    sample_chunk_size = main_client.settings["audio_sample_chunk_size"]
    sample_format = pyaudio.paInt16
    pa = pyaudio.PyAudio()
    stream_list = []
    for it in range(10):
        stream_list.append(pa.open(format=sample_format,
                                   channels=channels,
                                   rate=fs,
                                   output=True))


def play_audio_feed(payload):
    sound = pygame.mixer.Sound(payload)
    sound.play()


def audio_thread(payload):
    global stream_cycle
    stream = stream_list[stream_cycle]
    try:
        stream_cycle = (stream_cycle + 1) % 10
    except Exception as err:
        print(str(err))
    frames = functions.split_into_chunks(payload, 1024)
    for frame in frames:
        stream.write(frame)
