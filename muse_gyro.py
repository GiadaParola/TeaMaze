from pylsl import StreamInlet, resolve_byprop, resolve_streams

def main():
    print("🔍 Cerco lo stream GYRO del Muse 2...")

    streams = resolve_byprop('type', 'GYRO', timeout=5)

    if not streams:
        print("⚠️ Giroscopio non trovato. Ecco tutti gli stream disponibili:")
        all_streams = resolve_streams()
        for s in all_streams:
            print(f"- Name: {s.name()}, Type: {s.type()}, UID: {s.uid()}")
        return

    inlet = StreamInlet(streams[0])
    print("✅ Giroscopio connesso!")

if __name__ == "__main__":
    main()
