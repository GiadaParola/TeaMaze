import sys
import numpy as np
from scipy.signal import welch
import csv
from datetime import datetime

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from pylsl import StreamInlet, resolve_byprop, resolve_streams

# ---------------------------------------------------------------------------
# CONFIGURAZIONE
# ---------------------------------------------------------------------------

EEG_WINDOW_S = 5
MOTION_WINDOW_S = 5
PPG_WINDOW_S = 5

FS_EEG = 128
FS_MOTION = 52
FS_PPG = 64  # tipico per Muse PPG

REFRESH_MS = 40

EEG_CH_NAMES = ["TP9", "AF7", "AF8", "TP10"]
EEG_CH_COLORS = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]

ACCEL_LABELS = ["X", "Y", "Z"]
GYRO_LABELS = ["X", "Y", "Z"]
MOTION_COLORS = ["#EF553B", "#00CC96", "#636EFA"]

BANDS = {
    "Delta": (1, 4),
    "Theta": (4, 8),
    "Alpha": (8, 13),
    "Beta":  (13, 30),
}
BAND_COLORS = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]

# ---------------------------------------------------------------------------
# LSL
# ---------------------------------------------------------------------------

def resolve_muse_stream(stream_type, timeout=3.0):
    streams = resolve_byprop("type", stream_type, timeout=timeout)
    if streams:
        inlet = StreamInlet(streams[0], max_buflen=360, processing_flags=1)
        print(f"✅ {stream_type} connesso")
        return inlet
    print(f"⚠️  {stream_type} non trovato")
    return None

# ---------------------------------------------------------------------------
# RING BUFFER
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

        if n >= self.max_samples:
            self.data[:] = samples[-self.max_samples:]
            self.write_pos = 0
            self.full = True
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
# GUI
# ---------------------------------------------------------------------------

class MuseMonitor(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Muse 2 — EEG + Movimento + PPG")
        self.resize(1400, 1000)

        print("\n🔍 Ricerca stream LSL...\n")
        self.inlet_eeg = resolve_muse_stream("EEG")
        self.inlet_accel = resolve_muse_stream("Accelerometer")
        self.inlet_gyro = resolve_muse_stream("Gyroscope")
        self.inlet_ppg = resolve_muse_stream("PPG")

        if not any([self.inlet_eeg, self.inlet_accel, self.inlet_gyro, self.inlet_ppg]):
            print("\n❌ Nessuno stream trovato")
            for s in resolve_streams():
                print(f"- {s.name()} ({s.type()})")
            sys.exit(1)

        self.buf_eeg = RingBuffer(FS_EEG * EEG_WINDOW_S, 4)
        self.buf_eeg_fft = RingBuffer(256, 4)  # per Welch

        self.buf_accel = RingBuffer(FS_MOTION * MOTION_WINDOW_S, 3)
        self.buf_gyro = RingBuffer(FS_MOTION * MOTION_WINDOW_S, 3)
        self.buf_ppg = RingBuffer(FS_PPG * PPG_WINDOW_S, 1)

        # CSV per bande EEG + PPG
        self.csv_file = open("band_powers_ppg.csv", "w", newline="")
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Timestamp"] + list(BANDS.keys()) + ["PPG"])

        self._build_ui()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(REFRESH_MS)

        self.samples = 0

    # ---------------------------------------------------------------------

    def _build_ui(self):
        pg.setConfigOptions(background="#1e1e2e", foreground="#cdd6f4")

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)

        # EEG
        self.pw_eeg = pg.PlotWidget(title="EEG (µV)")
        self.pw_eeg.setYRange(-1000, 1000)
        self.pw_eeg.addLegend()
        self.pw_eeg.showGrid(x=True, y=True)
        self.eeg_curves = [
            self.pw_eeg.plot(pen=pg.mkPen(c, width=1), name=n)
            for n, c in zip(EEG_CH_NAMES, EEG_CH_COLORS)
        ]
        layout.addWidget(self.pw_eeg)

        # Bande EEG
        self.pw_bands = pg.PlotWidget(title="Potenza bande EEG")
        self.band_bars = pg.BarGraphItem(
            x=np.arange(len(BANDS)),
            height=np.zeros(len(BANDS)),
            width=0.6,
            brushes=[pg.mkBrush(c) for c in BAND_COLORS]
        )
        self.pw_bands.addItem(self.band_bars)
        self.pw_bands.setYRange(0, 1)
        self.pw_bands.getAxis("bottom").setTicks([list(enumerate(BANDS.keys()))])
        layout.addWidget(self.pw_bands)

        # Accelerometro
        self.pw_accel = pg.PlotWidget(title="Accelerometro (g)")
        self.pw_accel.addLegend()
        self.pw_accel.showGrid(x=True, y=True)
        self.accel_curves = [
            self.pw_accel.plot(pen=pg.mkPen(c, width=1.5), name=l)
            for l, c in zip(ACCEL_LABELS, MOTION_COLORS)
        ]
        layout.addWidget(self.pw_accel)

        # Giroscopio
        self.pw_gyro = pg.PlotWidget(title="Giroscopio (°/s)")
        self.pw_gyro.addLegend()
        self.pw_gyro.showGrid(x=True, y=True)
        self.gyro_curves = [
            self.pw_gyro.plot(pen=pg.mkPen(c, width=1.5), name=l)
            for l, c in zip(GYRO_LABELS, MOTION_COLORS)
        ]
        layout.addWidget(self.pw_gyro)

        # PPG
        self.pw_ppg = pg.PlotWidget(title="PPG")
        self.pw_ppg.showGrid(x=True, y=True)
        self.ppg_curve = self.pw_ppg.plot(pen=pg.mkPen("#FF00FF", width=1.5))
        layout.addWidget(self.pw_ppg)

        self.status = self.statusBar()

    # ---------------------------------------------------------------------

    def _pull(self, inlet, buf):
        if inlet is None:
            return 0

        samples, _ = inlet.pull_chunk(timeout=0.0, max_samples=1024)
        if samples:
            samples = np.array(samples)[:, :buf.n_channels]
            buf.append(samples)
            return len(samples)
        return 0

    # ---------------------------------------------------------------------

    def _band_powers(self):
        data = self.buf_eeg_fft.get()
        if len(data) < 64:
            return np.zeros(len(BANDS))

        powers = np.zeros(len(BANDS))
        total = 0

        for ch in range(4):
            freqs, psd = welch(data[:, ch], FS_EEG, nperseg=256)
            for i, (f1, f2) in enumerate(BANDS.values()):
                powers[i] += psd[(freqs >= f1) & (freqs <= f2)].sum()
            total += psd[(freqs >= 1) & (freqs <= 40)].sum()

        return powers / total if total > 0 else powers

    # ---------------------------------------------------------------------

    def _update(self):
        # --- Pull dati ---
        n = 0
        if self.inlet_eeg:
            samples, _ = self.inlet_eeg.pull_chunk(timeout=0.0, max_samples=1024)
            if samples:
                samples = np.array(samples)[:, :4]
                self.buf_eeg.append(samples)
                self.buf_eeg_fft.append(samples)
                n += len(samples)

        n += self._pull(self.inlet_accel, self.buf_accel)
        n += self._pull(self.inlet_gyro, self.buf_gyro)
        n += self._pull(self.inlet_ppg, self.buf_ppg)

        self.samples += n

        # --- EEG ---
        eeg = self.buf_eeg.get()
        if len(eeg) > 1:
            t = np.linspace(-len(eeg) / FS_EEG, 0, len(eeg))
            for i, c in enumerate(self.eeg_curves):
                c.setData(t, eeg[:, i])

        # --- Bande ---
        band_values = self._band_powers()
        self.band_bars.setOpts(height=band_values)

        # --- PPG ---
        ppg = self.buf_ppg.get()
        ppg_value = ppg[-1, 0] if len(ppg) > 0 else 0
        if len(ppg) > 1:
            t = np.linspace(-len(ppg) / FS_PPG, 0, len(ppg))
            self.ppg_curve.setData(t, ppg[:, 0])

        # --- Salvataggio CSV ---
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        self.csv_writer.writerow([timestamp] + band_values.tolist() + [ppg_value])

        # --- Stato ---
        if band_values[2] > 0.4:  # Alpha alta
            self.status.showMessage(f"Campioni: {self.samples:,} — 🧠 Focus rilevato! PPG: {ppg_value:.3f}")
        else:
            self.status.showMessage(f"Campioni: {self.samples:,} — PPG: {ppg_value:.3f}")

        # --- Accelerometro ---
        acc = self.buf_accel.get()
        if len(acc) > 1:
            t = np.linspace(-len(acc) / FS_MOTION, 0, len(acc))
            for i, c in enumerate(self.accel_curves):
                c.setData(t, acc[:, i])

        # --- Giroscopio ---
        gyr = self.buf_gyro.get()
        if len(gyr) > 1:
            t = np.linspace(-len(gyr) / FS_MOTION, 0, len(gyr))
            for i, c in enumerate(self.gyro_curves):
                c.setData(t, gyr[:, i])

    # ---------------------------------------------------------------------

    def closeEvent(self, event):
        self.timer.stop()
        if hasattr(self, "csv_file") and not self.csv_file.closed:
            self.csv_file.close()
        event.accept()

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MuseMonitor()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
