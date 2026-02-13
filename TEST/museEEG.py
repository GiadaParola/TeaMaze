import numpy as np
from scipy.signal import welch
from pylsl import StreamInlet, resolve_byprop
import time

class MuseEEG:
    FS_EEG = 128
    EEG_CH = 4
    EEG_WINDOW_S = 5

    BANDS = {
        "Delta": (1, 4),
        "Theta": (4, 8),
        "Alpha": (8, 13),
        "Beta":  (13, 30),
    }

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

    def __init__(self, fs=None, n_channels=None, window_s=None):
        self.fs = fs or self.FS_EEG
        self.n_channels = n_channels or self.EEG_CH
        self.window_s = window_s or self.EEG_WINDOW_S
        self.buffer = self.RingBuffer(self.fs * self.window_s, self.n_channels)
        self.inlet = None

    def connect(self, timeout=3.0):
        streams = resolve_byprop("type", "EEG", timeout=timeout)
        if streams:
            self.inlet = StreamInlet(streams[0])
            print("✅ EEG Muse connesso")
            return True
        else:
            print("⚠️ Nessun EEG trovato")
            return False

    def update(self):
        if not self.inlet:
            # Se non connesso, simuliamo dati per debug
            sample = np.random.randn(self.n_channels)
            sample = sample.reshape(1, self.n_channels)
            self.buffer.append(sample)
            return

        sample, ts = self.inlet.pull_sample(timeout=0.0)
        if sample:
            # Prendi solo i primi n_channels
            sample = np.array(sample[:self.n_channels]).reshape(1, self.n_channels)
            self.buffer.append(sample)

    def band_powers(self, data):
        if data.shape[0] < 32:
            return {band: 0.0 for band in self.BANDS}

        powers = np.zeros(len(self.BANDS))
        total_power = 0

        for ch in range(data.shape[1]):
            freqs, psd = welch(data[:, ch], fs=self.fs, nperseg=min(256, len(data)))
            for i, (f1, f2) in enumerate(self.BANDS.values()):
                powers[i] += psd[(freqs >= f1) & (freqs <= f2)].sum()
            total_power += psd[(freqs >= 1) & (freqs <= 40)].sum()

        if total_power > 0:
            powers /= total_power

        return dict(zip(self.BANDS.keys(), powers))

    def get_band_powers(self):
        data = self.buffer.get()
        return self.band_powers(data)

# ----------------- TEST -----------------
muse = MuseEEG()
# Chiamate ripetute per accumulare dati
for _ in range(200):
    muse.update()
    time.sleep(1/muse.fs)

print(muse.get_band_powers())
