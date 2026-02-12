import numpy as np
from scipy.signal import welch
from pylsl import StreamInlet, resolve_byprop

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

FS_EEG = 128  # Frequenza di campionamento Muse EEG
EEG_CH = 4    # Numero di canali EEG
EEG_WINDOW_S = 5  # Finestra di buffer in secondi

BANDS = {
    "Delta": (1, 4),
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta":  (13, 30),
}

# ---------------------------------------------------------------------------
# Ring buffer semplice
# ---------------------------------------------------------------------------

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
            self.full = True
        self.write_pos = end % self.max_samples
        if end >= self.max_samples:
            self.full = True

    def get(self):
        if not self.full:
            return self.data[:self.write_pos]
        return np.roll(self.data, -self.write_pos, axis=0)

# ---------------------------------------------------------------------------
# LSL: connetti Muse EEG
# ---------------------------------------------------------------------------

def resolve_muse_eeg():
    streams = resolve_byprop("type", "EEG", timeout=3.0)
    if streams:
        inlet = StreamInlet(streams[0])
        print("✅ EEG Muse connesso")
        return inlet
    else:
        print("⚠️ Nessun EEG trovato")
        return None

# ---------------------------------------------------------------------------
# Calcolo potenze delle bande
# ---------------------------------------------------------------------------

def band_powers(data, fs=FS_EEG):
    if len(data) < 64:
        return np.zeros(len(BANDS))

    powers = np.zeros(len(BANDS))
    total = 0

    for ch in range(data.shape[1]):
        freqs, psd = welch(data[:, ch], fs, nperseg=256)
        for i, (f1, f2) in enumerate(BANDS.values()):
            powers[i] += psd[(freqs >= f1) & (freqs <= f2)].sum()
        total += psd[(freqs >= 1) & (freqs <= 40)].sum()

    return powers / total if total > 0 else powers

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    inlet_eeg = resolve_muse_eeg()
    if inlet_eeg is None:
        exit()

    buf_eeg = RingBuffer(FS_EEG * EEG_WINDOW_S, EEG_CH)

    print("🔹 Lettura EEG Muse 2 — valori bande in tempo reale")
    try:
        while True:
            # Preleva i campioni dal Muse 2
            samples, _ = inlet_eeg.pull_chunk(timeout=1.0, max_samples=256)
            if samples:
                samples = np.array(samples)[:, :EEG_CH]
                buf_eeg.append(samples)

                # Calcola i valori delle bande
                eeg_data = buf_eeg.get()
                bands = band_powers(eeg_data)

                # Stampa a video
                #band_dict = {name: f"{val:.3f}" for name, val in zip(BANDS.keys(), bands)}
                print(f"Delta: {bands[0]:.3f} | Theta: {bands[1]:.3f} | Alpha: {bands[2]:.3f} | Beta: {bands[3]:.3f}")
    except KeyboardInterrupt:
        print("\n🔹 Uscita")