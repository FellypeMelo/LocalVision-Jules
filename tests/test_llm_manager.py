import unittest
from unittest.mock import patch, MagicMock
import queue
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_vision.logic.llm_manager import LLM_Manager

class TestLLMManager(unittest.TestCase):
    @patch('local_vision.logic.llm_manager.Client')
    def setUp(self, mock_client):
        """Set up the LLM_Manager with a mocked client."""
        self.llm_manager = LLM_Manager()
        # Mock the client instance and its methods
        self.mock_lmstudio_client = MagicMock()
        self.llm_manager.client = self.mock_lmstudio_client

    def test_get_text_response_formats_messages_correctly(self):
        """
        Tests that get_text_response formats the conversation history payload correctly.
        The 'content' for a text message should be a string, not a list.
        This test is expected to FAIL before the fix.
        """
        # 1. Define a sample conversation history
        conversation_history = [
            {'actor': 'user', 'type': 'text', 'content': 'Hello there!', 'image_path': None},
            {'actor': 'assistant', 'type': 'text', 'content': 'Hi! How can I help?', 'image_path': None}
        ]
        user_message = "What's the weather like?"
        result_queue = queue.Queue()

        # Mock the API response
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "It's sunny."
        self.mock_lmstudio_client.chat.completions.create.return_value = mock_completion

        # 2. Call the method under test
        with patch('threading.Thread') as mock_thread:
            target_worker = None
            def start_and_capture(target):
                nonlocal target_worker
                target_worker = target
                mock_thread_instance = MagicMock()
                mock_thread_instance.start.side_effect = target
                return mock_thread_instance

            mock_thread.side_effect = start_and_capture
            self.llm_manager.get_text_response(user_message, conversation_history, result_queue)
            self.assertIsNotNone(target_worker)

        # 3. Verify the payload sent to the mocked client
        self.mock_lmstudio_client.chat.completions.create.assert_called_once()
        call_args, call_kwargs = self.mock_lmstudio_client.chat.completions.create.call_args
        sent_messages = call_kwargs.get("messages", [])

        # 4. Assert the format of the conversation history
        self.assertEqual(len(sent_messages), 3)
        self.assertIsInstance(sent_messages[0]['content'], str)

if __name__ == '__main__':
    unittest.main()
