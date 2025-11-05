from PIL import Image
import customtkinter as ctk

class ImageProcessor:
    """
    Handles image processing tasks like validation and resizing.
    """
    @staticmethod
    def process_and_resize(filepath, max_size=(400, 400)):
        """
        Opens an image, validates it, resizes it, and returns a CTkImage.

        Args:
            filepath (str): The path to the image file.
            max_size (tuple): The maximum width and height for the image.

        Returns:
            CTkImage: A CustomTkinter-compatible image object, or None on error.
        """
        try:
            image = Image.open(filepath)
            image.thumbnail(max_size)

            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=image.size)
            return ctk_image
        except Exception as e:
            print(f"Error processing image: {e}")
            return None
