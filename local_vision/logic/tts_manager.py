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
        logging.info("TTS: _run_loop started")
        try:
            # Initialize COM for this thread (required for SAPI5 on Windows)
            try:
                import pythoncom
                pythoncom.CoInitialize()
                logging.debug("TTS: CoInitialize successful")
            except ImportError:
                logging.warning("TTS: pythoncom not found, skipping CoInitialize")
            except Exception as e:
                logging.error(f"TTS: Error in CoInitialize: {e}")

            logging.info("TTS: Initializing pyttsx3 engine...")
            
            # Initialize engine in the thread that uses it
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', 170)
                logging.info("TTS: Engine initialized successfully")
                
                # Start the event loop without blocking
                self.engine.startLoop(False)
                
            except Exception as e:
                logging.critical(f"TTS: Failed to initialize engine: {e}")
                return

            while self.is_running:
                try:
                    # Pump the engine loop
                    self.engine.iterate()
                    
                    # Check for new text
                    try:
                        text, interrupt = self.queue.get(block=False)
                        
                        logging.info(f"TTS: Processing '{text}' (interrupt={interrupt})")
                        
                        if interrupt:
                            try:
                                if self.engine.isBusy():
                                    logging.debug("TTS: Stopping current speech")
                                    self.engine.stop()
                            except Exception as e:
                                logging.warning(f"TTS: Error stopping engine: {e}")
                        
                        logging.info(f"TTS: Speaking: {text}")
                        self.engine.say(text)
                        
                    except queue.Empty:
                        # No new text, just sleep a bit to prevent CPU hogging
                        import time
                        time.sleep(0.05)
                        continue
                        
                except Exception as e:
                    logging.error(f"TTS: Error in loop: {e}", exc_info=True)
                    # Re-initialize engine on error
                    try:
                        logging.warning("TTS: Attempting to re-initialize engine...")
                        if self.engine:
                            self.engine.endLoop()
                        self.engine = pyttsx3.init()
                        self.engine.setProperty('rate', 170)
                        self.engine.startLoop(False)
                        logging.info("TTS: Engine re-initialized")
                    except Exception as re_init_error:
                        logging.error(f"TTS: Failed to re-initialize TTS: {re_init_error}")
                        import time
                        time.sleep(1) # Prevent tight loop on failure
                    
        except Exception as e:
            logging.critical(f"TTS: Fatal error in TTS thread: {e}", exc_info=True)
        finally:
            logging.info("TTS: Thread ending")
            if self.engine:
                try:
                    self.engine.endLoop()
                except:
                    pass
            try:
                import pythoncom
                pythoncom.CoUninitialize()
            except:
                pass

    def speak(self, text, interrupt=True):
        """Queue text to be spoken."""
        if not text:
            return
        
        # Check if thread is alive
        if not self.thread.is_alive():
            logging.critical("TTS: Thread is DEAD! Attempting to restart...")
            try:
                self.is_running = True
                self.thread = threading.Thread(target=self._run_loop, daemon=True)
                self.thread.start()
            except Exception as e:
                logging.error(f"TTS: Failed to restart thread: {e}")

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
            try:
                self.engine.stop()
            except:
                pass

    def shutdown(self):
        """Shutdown the TTS manager."""
        logging.info("TTS: Shutdown requested")
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join(timeout=2.0)
