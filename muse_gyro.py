from pylsl import StreamInlet, resolve_byprop, resolve_streams
import time

def main():
    print("🔍 Cerco lo stream Gyroscope del Muse 2...")

    # Attenzione alla case: "Gyroscope" non "GYRO"
    streams = resolve_byprop('type', 'Gyroscope', timeout=5)

    if not streams:
        print("⚠️ Giroscopio non trovato. Ecco tutti gli stream disponibili:")
        all_streams = resolve_streams()
        for s in all_streams:
            print(f"- Name: {s.name()}, Type: {s.type()}, UID: {s.uid()}")
        return

    inlet = StreamInlet(streams[0])
    print("✅ Giroscopio connesso!")

    # Legge i dati in tempo reale
    print("📊 Leggo dati dal giroscopio (CTRL+C per fermare):")
    try:
        while True:
            sample, timestamp = inlet.pull_sample()
            print(f"{timestamp:.3f}: {sample}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Lettura interrotta dall'utente.")

if __name__ == "__main__":
    main()
