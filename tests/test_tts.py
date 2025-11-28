import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import queue

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_vision.logic.tts_manager import TTSManager

class TestTTSManager(unittest.TestCase):
    def setUp(self):
        TTSManager._instance = None
        self.mock_pyttsx3 = MagicMock()
        self.mock_engine = MagicMock()
        self.mock_pyttsx3.init.return_value = self.mock_engine
        
        with patch('local_vision.logic.tts_manager.pyttsx3', self.mock_pyttsx3):
            with patch('threading.Thread'):
                self.tts_manager = TTSManager()
                self.tts_manager.engine = self.mock_engine

    def tearDown(self):
        self.tts_manager.shutdown()
        TTSManager._instance = None

    def test_singleton(self):
        with patch('threading.Thread'):
            manager2 = TTSManager()
            self.assertIs(self.tts_manager, manager2)

    def test_initialization(self):
        self.assertTrue(self.tts_manager.is_running)
        self.assertTrue(self.tts_manager.enabled)
        self.assertIsInstance(self.tts_manager.queue, queue.Queue)

    def test_speak_enabled(self):
        self.tts_manager.speak("Hello")
        item = self.tts_manager.queue.get()
        self.assertEqual(item, ("Hello", True))

    def test_speak_disabled(self):
        self.tts_manager.enabled = False
        self.tts_manager.speak("Hello")
        self.assertTrue(self.tts_manager.queue.empty())

    def test_speak_empty_text(self):
        self.tts_manager.speak("")
        self.assertTrue(self.tts_manager.queue.empty())

    def test_stop(self):
        self.tts_manager.queue.put(("Hello", True))
        self.tts_manager.stop()
        self.assertTrue(self.tts_manager.queue.empty())
        self.mock_engine.stop.assert_called()

    def test_shutdown(self):
        with patch('threading.Thread') as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance
            self.tts_manager.thread = mock_thread_instance
            
            self.tts_manager.shutdown()
            self.assertFalse(self.tts_manager.is_running)
            mock_thread_instance.join.assert_called()

if __name__ == '__main__':
    unittest.main()
