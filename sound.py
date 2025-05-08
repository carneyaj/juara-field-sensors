import sounddevice as sd
import numpy as np
import threading

class Stream:
    def __init__(self, duration=3, sr=48000, channels=1, device=None):
        sd.default.samplerate = sr
        sd.default.channels = channels
        self.sr = sr
        self.channels = channels
        self.buffer_size = sr * duration
        self.buffer = np.zeros((self.buffer_size, channels), dtype='float32')
        self.idx = 0
        self.lock = threading.Lock()
        self.device = device

    def audio_callback(self, indata, frames, *_):
        with self.lock:
            end = (self.idx + frames) % self.buffer_size
            if self.idx + frames <= self.buffer_size:
                self.buffer[self.idx:self.idx+frames] = indata
            else:
                split = self.buffer_size - self.idx
                self.buffer[self.idx:] = indata[:split]
                self.buffer[:end] = indata[split:]
            self.idx = end

    def normalize(self, data):
        return data - np.mean(data, axis=0)

    def get_audio(self):
        with self.lock:
            return self.normalize(np.roll(self.buffer, -self.idx, axis=0).flatten())

    def start(self):
        self.stream = sd.InputStream(
            samplerate=self.sr,
            channels=self.channels,
            callback=self.audio_callback,
            blocksize=4096,
            device=self.device
        )
        self.stream.start()

    def stop(self):
        self.stream.stop()
        self.stream.close()


    def record_nb(self, seconds):
        self.data = sd.rec(self.sr * seconds, device=self.device)

    def record_wait(self):
        sd.wait()
        return(self.normalize(self.data.reshape(-1)))

