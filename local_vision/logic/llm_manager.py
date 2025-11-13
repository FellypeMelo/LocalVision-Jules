from lmstudio import Client
from PIL import Image
import base64
from io import BytesIO
import threading
import queue

class LLM_Manager:
    """
    Manages interactions with the LM Studio local server, including
    image description generation and contextual chat in separate threads.
    """
    def __init__(self, model_identifier="local-model", base_url="http://localhost:1234/v1"):
        """
        Initializes the LLM_Manager.

        Args:
            model_identifier (str): The identifier for the model to use.
            base_url (str): The base URL of the LM Studio server.
        """
        self.client = Client()
        self.model_identifier = model_identifier

    def _image_to_base64(self, image_path):
        """Converts an image file to a base64 encoded string."""
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def get_image_description(self, image_path, result_queue):
        """
        Generates a description for an image in a separate thread.

        Args:
            image_path (str): The path to the image file.
            result_queue (queue.Queue): The queue to put the result in.
        """
        def worker():
            try:
                img_base64 = self._image_to_base64(image_path)

                completion = self.client.chat.completions.create(
                    model=self.model_identifier,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Describe this image in detail."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}},
                            ],
                        }
                    ],
                    max_tokens=1000,
                )
                description = completion.choices[0].message.content
                result_queue.put({"type": "description", "content": description})
            except Exception as e:
                result_queue.put({"type": "error", "content": f"Error: {e}"})

        thread = threading.Thread(target=worker)
        thread.start()

    def get_text_response(self, message, conversation_history, result_queue):
        """
        Generates a contextual text response based on the conversation history.

        Args:
            message (str): The user's new text message.
            conversation_history (list): A list of previous interaction dicts.
            result_queue (queue.Queue): The queue to put the result in.
        """
        def worker():
            try:
                messages = []
                # Construct the message history for the model
                for interaction in conversation_history:
                    role = "user" if interaction['actor'] == 'user' else "assistant"

                    if interaction['type'] == 'text' or interaction['type'] == 'description':
                        # For text and description, content is a simple string
                        messages.append({"role": role, "content": interaction['content']})
                    elif interaction['type'] == 'image':
                        # For images, content is a list of parts
                        img_base64 = self._image_to_base64(interaction['image_path'])
                        content = [
                            {"type": "text", "text": "Here is an image."}, # Placeholder text
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                        ]
                        messages.append({"role": role, "content": content})

                # Add the new user message
                messages.append({"role": "user", "content": message})

                completion = self.client.chat.completions.create(
                    model=self.model_identifier,
                    messages=messages,
                    max_tokens=500,
                )
                response = completion.choices[0].message.content
                result_queue.put({"type": "text_response", "content": response})
            except Exception as e:
                result_queue.put({"type": "error", "content": f"Error: {e}"})

        thread = threading.Thread(target=worker)
        thread.start()
