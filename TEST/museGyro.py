import numpy as np
from muse import Muse

class MuseGYRO(Muse):
    FS_GYRO = 52
    GYRO_CH = 3

    def __init__(self, fs=None, n_channels=None, window_s=5, soglia_picco=1.0):
        super().__init__(
            stream_type="Gyroscope",
            fs=fs or self.FS_GYRO,
            n_channels=n_channels or self.GYRO_CH,
            window_s=window_s
        )
        self.soglia_picco = soglia_picco  # soglia per rilevare picchi

    def get_xyz(self):
        latest = self.get_latest()
        return {"x": latest[0], "y": latest[1], "z": latest[2]}

    def get_mean(self):
        data = self.buffer.get()
        if len(data) == 0:
            return {"x": 0, "y": 0, "z": 0}
        mean_vals = np.mean(data, axis=0)
        return {"x": mean_vals[0], "y": mean_vals[1], "z": mean_vals[2]}

    def picco_positivo(self, asse):
        """Ritorna True se c'è stato un picco positivo nell'asse"""
        idx = {"x": 0, "y": 1, "z": 2}[asse]
        data = self.buffer.get()
        if len(data) == 0:
            return False
        # Picco positivo: valore massimo recente > soglia
        return np.max(data[:, idx]) > self.soglia_picco

    def picco_negativo(self, asse):
        """Ritorna True se c'è stato un picco negativo nell'asse"""
        idx = {"x": 0, "y": 1, "z": 2}[asse]
        data = self.buffer.get()
        if len(data) == 0:
            return False
        # Picco negativo: valore minimo recente < -soglia
        return np.min(data[:, idx]) < -self.soglia_picco
