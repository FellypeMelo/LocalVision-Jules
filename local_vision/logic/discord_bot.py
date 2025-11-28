import discord
import threading
import asyncio
import os
import tempfile
import logging
from local_vision.logic.llm_manager import LLM_Manager

class DiscordBot(discord.Client):
    """
    A simple Discord bot that listens for images and replies with descriptions.
    """
    def __init__(self, token, llm_manager: LLM_Manager):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        
        self.token = token
        self.llm_manager = llm_manager
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.is_running = False

    def start_bot(self):
        """Starts the bot in a separate thread."""
        if not self.is_running:
            self.is_running = True
            self.thread.start()

    def stop_bot(self):
        """Stops the bot."""
        if self.is_running:
            self.is_running = False
            asyncio.run_coroutine_threadsafe(self.close(), self.loop)
            self.thread.join(timeout=2.0)

    def _run_loop(self):
        """Runs the asyncio loop for the bot."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.start(self.token))
        except Exception as e:
            logging.error(f"Discord Bot Error: {e}")
        finally:
            self.loop.close()

    async def on_ready(self):
        logging.info(f'Discord Bot connected as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.attachments:
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    await self._process_image(message, attachment)

    async def _process_image(self, message, attachment):
        """Downloads image, gets description, and replies."""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                await attachment.save(temp_file.name)
                temp_path = temp_file.name

            import queue
            temp_queue = queue.Queue()
            
            self.llm_manager.get_image_description(temp_path, temp_queue)
            
            response = await self.loop.run_in_executor(None, temp_queue.get)
            
            if response['type'] == 'description':
                await message.reply(f"**Análise da Imagem:**\n{response['content']}")
            else:
                await message.reply(f"Erro ao analisar imagem: {response.get('content')}")

            if os.path.exists(temp_path):
                os.remove(temp_path)

        except Exception as e:
            logging.error(f"Error processing Discord image: {e}")
            await message.reply("Ocorreu um erro ao processar sua imagem.")
