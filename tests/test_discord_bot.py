import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_vision.logic.discord_bot import DiscordBot

class TestDiscordBot(unittest.TestCase):
    def setUp(self):
        self.mock_llm_manager = MagicMock()
        with patch('discord.Client'):
            self.bot = DiscordBot("fake_token", self.mock_llm_manager)

    def test_init(self):
        self.assertEqual(self.bot.token, "fake_token")
        self.assertEqual(self.bot.llm_manager, self.mock_llm_manager)
        self.assertFalse(self.bot.is_running)

    def test_start_bot(self):
        self.bot.thread = MagicMock()
        self.bot.start_bot()
        self.assertTrue(self.bot.is_running)
        self.bot.thread.start.assert_called_once()

    @patch('asyncio.run_coroutine_threadsafe')
    def test_stop_bot(self, mock_run_coroutine):
        self.bot.is_running = True
        self.bot.thread = MagicMock()
        self.bot.stop_bot()
        self.assertFalse(self.bot.is_running)
        self.bot.thread.join.assert_called()

    @patch('local_vision.logic.discord_bot.tempfile.NamedTemporaryFile')
    @patch('os.remove')
    @patch('os.path.exists')
    def test_process_image_success(self, mock_exists, mock_remove, mock_tempfile):
        async def run_test():
            mock_message = MagicMock()
            mock_message.reply = AsyncMock()
            mock_attachment = MagicMock()
            mock_attachment.save = AsyncMock()
            
            mock_temp = MagicMock()
            mock_temp.name = "temp.png"
            mock_tempfile.return_value.__enter__.return_value = mock_temp
            
            mock_exists.return_value = True
            
            self.bot.loop = MagicMock()
            self.bot.loop.run_in_executor = AsyncMock(return_value={'type': 'description', 'content': 'A cat'})
            
            await self.bot._process_image(mock_message, mock_attachment)
            
            self.mock_llm_manager.get_image_description.assert_called()
            mock_message.reply.assert_called_with("**Análise da Imagem:**\nA cat")
            mock_remove.assert_called_with("temp.png")

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
