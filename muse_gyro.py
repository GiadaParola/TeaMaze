from pylsl import StreamInlet, resolve_byprop, resolve_streams
import time

def main():
    print("🔍 Cerco lo stream Gyroscope del Muse 2...")

    # - Name: Muse-4A32 (00:55:da:b5:4a:32) EEG, Type: EEG, UID: 47a40b63-7d6b-46a4-bd24-67cde41abe04
    # - Name: Muse-4A32 (00:55:da:b5:4a:32) Accelerometer, Type: Accelerometer, UID: 54ba1491-8b40-4f3d-9cb6-02b508b42c8d
    # - Name: Muse-4A32 (00:55:da:b5:4a:32) Gyroscope, Type: Gyroscope, UID: 5a43ce47-de70-4505-8cfe-1cfb7df4018a
    # - Name: Muse-4A32 (00:55:da:b5:4a:32) PPG, Type: PPG, UID: ed815c93-f8de-4c1a-8372-639e7e84bb1d
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
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\n🛑 Lettura interrotta dall'utente.")

if __name__ == "__main__":
    main()
