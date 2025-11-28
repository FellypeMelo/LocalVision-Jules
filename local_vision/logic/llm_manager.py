import lmstudio as lms
import threading
import queue
import logging

class LLM_Manager:
    """
    Manages interactions with the LM Studio local server using the native lmstudio SDK.
    """
    def __init__(self, model_identifier="local-model", base_url="http://localhost:1234/v1"):
        """
        Initializes the LLM_Manager.
        """
        host_port = base_url.replace("http://", "").replace("https://", "").replace("/v1", "").strip()
        
        logging.debug(f"LLM_Manager: Connecting to {host_port}")
        self.client = lms.Client(api_host=host_port)
        
        logging.debug(f"LLM_Manager: Getting model {model_identifier}")
        self.model = self.client.llm.model(model_identifier)

    def _execute_with_retry(self, func, *args, **kwargs):
        """
        Executes a function with retry logic for connection errors.
        """
        max_retries = 3
        import time
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_str = str(e).lower()
                if "econnreset" in error_str or "connection" in error_str or "timeout" in error_str:
                    logging.warning(f"Connection error (attempt {attempt+1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1 * (attempt + 1))
                        try:
                            host_port = self.client.api_host
                            self.client = lms.Client(api_host=host_port)
                            self.model = self.client.llm.model(self.model.identifier)
                        except:
                            pass
                        continue
                raise e

    def _strip_markdown(self, text):
        """
        Removes Markdown formatting from the text to make it cleaner for the UI.
        """
        import re
        text = re.sub(r'(\*\*|__)(.*?)\1', r'\2', text)
        text = re.sub(r'(\*|_)(.*?)\1', r'\2', text)
        
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`(.*?)`', r'\1', text)
        
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        return text.strip()

    def get_image_description(self, image_path, result_queue):
        """
        Generates a description for an image in a separate thread.
        """
        def worker():
            try:
                def _task():
                    chat = lms.Chat("You are an image analysis assistant.")
                    image_handle = self.client.prepare_image(src=image_path)
                    chat.add_user_message([
                        "Descreva esta imagem detalhadamente em português. Seja preciso e inclua detalhes visuais importantes.",
                        image_handle
                    ])
                    return self.model.respond(chat)

                result = self._execute_with_retry(_task)
                description = self._strip_markdown(result.content)
                result_queue.put({"type": "description", "content": description})
            except Exception as e:
                result_queue.put({"type": "error", "content": f"An unexpected error occurred: {e}"})

        thread = threading.Thread(target=worker)
        thread.start()

    def get_text_response(self, message, conversation_history, result_queue):
        """
        Generates a contextual text response based on the conversation history.
        """
        def worker():
            try:
                def _task():
                    chat = lms.Chat("You are a helpful AI assistant.")

                    for interaction in conversation_history:
                        actor = interaction['actor']
                        content = interaction['content']

                        if actor == 'user':
                            if interaction['type'] == 'image':
                                try:
                                    image_handle = self.client.prepare_image(src=interaction['image_path'])
                                    prompt = content if isinstance(content, str) and content else "Here is the image again."
                                    chat.add_user_message([prompt, image_handle])
                                except:
                                    chat.add_user_message("[Image missing] " + str(content))
                            else:
                                chat.add_user_message(content)
                        elif actor == 'assistant':
                            if interaction['type'] == 'description' or interaction['type'] == 'text_response':
                                 chat.add_assistant_response(content)

                    chat.add_user_message(message)

                    return self.model.respond(chat)

                result = self._execute_with_retry(_task)
                response = self._strip_markdown(result.content)
                result_queue.put({"type": "text_response", "content": response})
            except Exception as e:
                result_queue.put({"type": "error", "content": f"An unexpected error occurred: {e}"})

        thread = threading.Thread(target=worker)
        thread.start()
