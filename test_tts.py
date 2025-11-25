import pyttsx3
import time
import threading
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def test_basic_tts():
    print("\n--- Testing Basic TTS (Main Thread) ---")
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        print(f"Found {len(voices)} voices.")
        for v in voices:
            print(f" - {v.name} ({v.id})")
            
        print("Speaking: 'Testing basic text to speech'")
        engine.say("Testing basic text to speech")
        engine.runAndWait()
        print("Basic TTS complete.")
    except Exception as e:
        print(f"Basic TTS Failed: {e}")

def threaded_tts_worker():
    print("\n--- Testing Threaded TTS ---")
    try:
        import pythoncom
        pythoncom.CoInitialize()
        print("CoInitialize successful")
    except Exception as e:
        print(f"CoInitialize failed: {e}")
        
    try:
        engine = pyttsx3.init()
        print("Threaded engine initialized")
        print("Speaking: 'Testing threaded text to speech'")
        engine.say("Testing threaded text to speech")
        engine.runAndWait()
        print("Threaded TTS complete.")
    except Exception as e:
        print(f"Threaded TTS Failed: {e}")
    finally:
        try:
            import pythoncom
            pythoncom.CoUninitialize()
        except:
            pass

def test_threaded_tts():
    t = threading.Thread(target=threaded_tts_worker)
    t.start()
    t.join()

if __name__ == "__main__":
    test_basic_tts()
    test_threaded_tts()
    print("\nDone.")
