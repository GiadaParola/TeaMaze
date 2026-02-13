from scipy.signal import welch
import numpy as np
from muse import Muse
import time

class MuseEEG(Muse):
    FS_EEG = 128
    EEG_CH = 4

    BANDS = {
        "Delta": (1, 4),
        "Theta": (4, 8),
        "Alpha": (8, 13),
        "Beta":  (13, 30),
    }

    def __init__(self, fs=None, n_channels=None, window_s=5):
        super().__init__(
            stream_type="EEG",
            fs=fs or self.FS_EEG,
            n_channels=n_channels or self.EEG_CH,
            window_s=window_s
        )

    # --------------------------------------------------

    def band_powers(self, data):
        if data is None or len(data) < 32:
            return {band: 0.0 for band in self.BANDS}

        powers = np.zeros(len(self.BANDS))
        total_power = 0.0

        for ch in range(data.shape[1]):
            freqs, psd = welch(
                data[:, ch],
                fs=self.fs,
                nperseg=min(256, len(data))
            )

            # Potenza per banda
            for i, (f1, f2) in enumerate(self.BANDS.values()):
                mask = (freqs >= f1) & (freqs <= f2)
                powers[i] += np.sum(psd[mask])

            # Potenza totale 1–40 Hz
            total_mask = (freqs >= 1) & (freqs <= 40)
            total_power += np.sum(psd[total_mask])

        if total_power > 0:
            powers /= total_power

        return dict(zip(self.BANDS.keys(), powers))

    def get_band_powers(self):
        data = self.buffer.get()
        return self.band_powers(data)


# ----------------- TEST -----------------
muse = MuseEEG()

# Accumula dati
for _ in range(200):
    muse.update()
    time.sleep(1 / muse.fs)

print(muse.get_band_powers())
