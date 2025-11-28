import unittest
import os
import sys
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_vision.data.history_manager import HistoryManager

class TestHistoryManager(unittest.TestCase):
    def setUp(self):
        self.mock_db_manager = MagicMock()
        self.history_manager = HistoryManager(self.mock_db_manager)

    def test_create_conversation(self):
        self.mock_db_manager.execute_crud_query.return_value = 1
        conversation_id = self.history_manager.create_conversation("TestUser")
        self.assertEqual(conversation_id, 1)
        self.mock_db_manager.execute_crud_query.assert_called_once()
        args, _ = self.mock_db_manager.execute_crud_query.call_args
        self.assertIn("INSERT INTO conversations", args[0])
        self.assertIn("TestUser", args[1])

    def test_save_interaction(self):
        self.history_manager.save_interaction(1, "user", "text", "Hello")
        self.mock_db_manager.execute_crud_query.assert_called_once()
        args, _ = self.mock_db_manager.execute_crud_query.call_args
        self.assertIn("INSERT INTO interactions", args[0])
        self.assertEqual(args[1][0], 1)
        self.assertEqual(args[1][2], "user")
        self.assertEqual(args[1][4], "Hello")

    def test_get_conversations(self):
        self.mock_db_manager.execute_crud_query.return_value = []
        self.history_manager.get_conversations()
        self.mock_db_manager.execute_crud_query.assert_called_once()
        args, _ = self.mock_db_manager.execute_crud_query.call_args
        self.assertIn("SELECT * FROM conversations", args[0])

    def test_get_conversation_history(self):
        mock_history = [
            (1, 1, "2023-01-01", "user", "text", "Hello", None)
        ]
        self.mock_db_manager.execute_crud_query.return_value = mock_history
        
        history = self.history_manager.get_conversation_history(1)
        self.assertEqual(history, mock_history)

        dict_history = self.history_manager.get_conversation_history(1, as_dict=True)
        self.assertEqual(len(dict_history), 1)
        self.assertEqual(dict_history[0]['content'], "Hello")

    def test_delete_conversation(self):
        self.history_manager.delete_conversation(1)
        self.assertEqual(self.mock_db_manager.execute_crud_query.call_count, 2)

if __name__ == '__main__':
    unittest.main()
