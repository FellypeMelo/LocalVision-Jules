import unittest
from unittest.mock import patch, MagicMock
import queue
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_vision.logic.llm_manager import LLM_Manager

class TestLLMManager(unittest.TestCase):
    def setUp(self):
        self.lms_patcher = patch('local_vision.logic.llm_manager.lms')
        self.mock_lms = self.lms_patcher.start()
        
        self.mock_client = MagicMock()
        self.mock_lms.Client.return_value = self.mock_client
        self.llm_manager = LLM_Manager()
        self.llm_manager.client = self.mock_client
        self.llm_manager.model = MagicMock()
        
        # Mock Chat
        self.mock_chat = MagicMock()
        self.mock_lms.Chat.return_value = self.mock_chat

    def tearDown(self):
        self.lms_patcher.stop()

    def test_get_text_response_formats_messages_correctly(self):
        conversation_history = [
            {'actor': 'user', 'type': 'text', 'content': 'Hello there!', 'image_path': None},
            {'actor': 'assistant', 'type': 'text', 'content': 'Hi! How can I help?', 'image_path': None}
        ]
        user_message = "What's the weather like?"
        result_queue = queue.Queue()

        mock_response = MagicMock()
        mock_response.content = "It's sunny."
        self.llm_manager.model.respond.return_value = mock_response

        with patch('threading.Thread') as mock_thread:
            mock_thread.side_effect = lambda target: MagicMock(start=lambda: target())
            self.llm_manager.get_text_response(user_message, conversation_history, result_queue)

        result = result_queue.get()
        if result['type'] == 'error':
            self.fail(f"Got error response: {result['content']}")
            
        self.assertEqual(result['type'], 'text_response')
        self.assertEqual(result['content'], "It's sunny.")
        self.llm_manager.model.respond.assert_called_once()

    def test_get_image_description(self):
        image_path = "test_image.png"
        result_queue = queue.Queue()

        mock_response = MagicMock()
        mock_response.content = "A beautiful landscape."
        self.llm_manager.model.respond.return_value = mock_response

        with patch('threading.Thread') as mock_thread:
            mock_thread.side_effect = lambda target: MagicMock(start=lambda: target())
            self.llm_manager.get_image_description(image_path, result_queue)

        result = result_queue.get()
        if result['type'] == 'error':
            with open('test_failure.txt', 'w') as f:
                f.write(result['content'])
            self.fail(f"Got error response: {result['content']}")

        self.assertEqual(result['type'], 'description')
        self.assertEqual(result['content'], "A beautiful landscape.")
        self.llm_manager.client.prepare_image.assert_called_with(src=image_path)

    def test_error_handling(self):
        result_queue = queue.Queue()
        self.llm_manager.model.respond.side_effect = Exception("API Error")

        with patch('threading.Thread') as mock_thread:
            mock_thread.side_effect = lambda target: MagicMock(start=lambda: target())
            self.llm_manager.get_text_response("Hi", [], result_queue)

        result = result_queue.get()
        self.assertEqual(result['type'], 'error')
        self.assertIn("API Error", result['content'])

if __name__ == '__main__':
    unittest.main()
