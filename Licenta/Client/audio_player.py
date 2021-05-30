import pyaudio
from Utils import functions
import main_client

channels = None
fs = None
sample_chunk_size = None
sample_format = None
pa = None
stream = None


def init():
    global channels
    global fs
    global sample_chunk_size
    global sample_format
    global pa
    global stream
    channels = main_client.settings["audio_channels"]
    fs = main_client.settings["audio_fs"]
    sample_chunk_size = main_client.settings["audio_sample_chunk_size"]
    sample_format = pyaudio.paInt16
    pa = pyaudio.PyAudio()
    stream = pa.open(format=sample_format,
                     channels=channels,
                     rate=fs,
                     output=True)


def play_audio_feed(payload):
    frames = functions.split_into_chunks(payload, 4096)
    for frame in frames:
        stream.write(frame)
