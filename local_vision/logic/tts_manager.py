import pyttsx3
import threading
import queue
import logging

class TTSManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TTSManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.engine = None
        self.queue = queue.Queue()
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logging.info("TTSManager initialized")

    def _run_loop(self):
        """Background thread loop for TTS engine."""
        try:
            # Initialize engine in the thread that uses it
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 170) # Slightly faster than default
            
            while self.is_running:
                try:
                    # Get text from queue
                    text, interrupt = self.queue.get(timeout=0.5)
                    
                    if interrupt:
                        try:
                            if self.engine.isBusy():
                                self.engine.stop()
                        except:
                            pass
                    
                    logging.debug(f"TTS Speaking: {text}")
                    self.engine.say(text)
                    self.engine.runAndWait()
                    
                except queue.Empty:
                    # Process events to keep engine responsive
                    try:
                        self.engine.runAndWait()
                    except:
                        pass
                    continue
                except Exception as e:
                    logging.error(f"Error in TTS loop: {e}")
                    # Re-initialize engine on error
                    try:
                        self.engine = pyttsx3.init()
                        self.engine.setProperty('rate', 170)
                    except:
                        pass
                    
        except Exception as e:
            logging.error(f"Fatal error in TTS thread: {e}")

    def speak(self, text, interrupt=True):
        """Queue text to be spoken."""
        if not text:
            return
        
        logging.info(f"TTS.speak() called with: '{text}' (interrupt={interrupt})")
        
        # Clear queue if interrupting
        if interrupt:
            with self.queue.mutex:
                self.queue.queue.clear()
        
        self.queue.put((text, interrupt))

    def stop(self):
        """Stop speaking immediately."""
        with self.queue.mutex:
            self.queue.queue.clear()
        if self.engine:
            self.engine.stop()

    def shutdown(self):
        """Shutdown the TTS manager."""
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join(timeout=2.0)
