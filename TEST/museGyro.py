from muse import Muse

class MuseGyro(Muse):
    FS_GYRO = 52
    GYRO_CH = 3

    def __init__(self, fs=None, n_channels=None, window_s=5):
        super().__init__(
            stream_type="Gyroscope",
            fs=fs or self.FS_GYRO,
            n_channels=n_channels or self.GYRO_CH,
            window_s=window_s
        )

    def get_xyz(self):
        latest = self.get_latest()
        return {
            "x": latest[0],
            "y": latest[1],
            "z": latest[2],
        }

    def get_mean(self):
        """
        Restituisce la media della finestra corrente
        (utile per controllo movimento stabile)
        """
        data = self.buffer.get()
        if len(data) == 0:
            return {"x": 0, "y": 0, "z": 0}

        mean_vals = np.mean(data, axis=0)
        return {"x": mean_vals[0], "y": mean_vals[1], "z": mean_vals[2]}
