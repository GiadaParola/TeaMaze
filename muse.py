import numpy as np
from pylsl import StreamInlet, resolve_byprop
import sys

class Muse:
    # Classe base generica per stream Muse via LSL.
    # EEG, Gyro, Accelerometro possono ereditarla.

    class RingBuffer:
        def __init__(self, max_samples, n_channels):
            self.max_samples = max_samples
            self.n_channels = n_channels
            self.data = np.zeros((max_samples, n_channels))
            self.write_pos = 0
            self.full = False

        def append(self, samples):
            n = samples.shape[0]
            if n == 0:
                return

            end = self.write_pos + n
            if end <= self.max_samples:
                self.data[self.write_pos:end] = samples
            else:
                first = self.max_samples - self.write_pos
                self.data[self.write_pos:] = samples[:first]
                self.data[:n - first] = samples[first:]

            self.write_pos = end % self.max_samples
            if end >= self.max_samples:
                self.full = True

        def get(self):
            if not self.full:
                return self.data[:self.write_pos]
            return np.roll(self.data, -self.write_pos, axis=0)

    # --------------------------------------------------

    def __init__(self, stream_type, fs, n_channels, window_s=5):
        self.stream_type = stream_type
        self.fs = fs
        self.n_channels = n_channels
        self.window_s = window_s
        self.buffer = self.RingBuffer(self.fs * self.window_s, self.n_channels)
        self.inlet = None

    # --------------------------------------------------

    def connect(self, timeout=3.0):
        print(f"🔎 Ricerca stream {self.stream_type}...")
        streams = resolve_byprop("type", self.stream_type, timeout=timeout)

        if streams:
            self.inlet = StreamInlet(streams[0])
            print(f"✅ Muse {self.stream_type} connesso")
            return True
        else:
            print(f"❌ Nessuno stream {self.stream_type} trovato. Il programma si interrompe.")
            sys.exit(1)  # blocca il programma

    # --------------------------------------------------

    def update(self):
        # Legge un campione dallo stream.
        # Se non connesso → simula dati.
        
        if not self.inlet:
            sample = np.random.randn(self.n_channels)
            self.buffer.append(sample.reshape(1, self.n_channels))
            return

        sample, ts = self.inlet.pull_sample(timeout=0.0)

        if sample:
            sample = np.array(sample[:self.n_channels]).reshape(1, self.n_channels)
            self.buffer.append(sample)

    # --------------------------------------------------

    def get_data(self):
        # Restituisce tutto il buffer corrente
        return self.buffer.get()

    # --------------------------------------------------

    def get_latest(self):
        # Restituisce l’ultimo campione
        data = self.buffer.get()
        if len(data) == 0:
            return np.zeros(self.n_channels)
        return data[-1]

    def clear_buffer(self):
        # Svuota il buffer
        self.buffer.data[:] = 0          # azzera tutti i dati
        self.buffer.write_pos = 0        # resetta la posizione di scrittura
        self.buffer.full = False         # indica che il buffer non è pieno
