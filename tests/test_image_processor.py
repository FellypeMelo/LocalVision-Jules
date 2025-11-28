import unittest
from unittest.mock import MagicMock, patch
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_vision.logic.image_processor import ImageProcessor

class TestImageProcessor(unittest.TestCase):
    @patch('local_vision.logic.image_processor.Image')
    @patch('local_vision.logic.image_processor.ctk.CTkImage')
    def test_process_and_resize_success(self, mock_ctk_image, mock_pil_image):
        mock_img_instance = MagicMock()
        mock_pil_image.open.return_value = mock_img_instance
        mock_img_instance.size = (800, 600)
        
        result = ImageProcessor.process_and_resize("test.jpg")
        
        mock_pil_image.open.assert_called_with("test.jpg")
        mock_img_instance.thumbnail.assert_called_with((400, 400))
        mock_ctk_image.assert_called()
        self.assertIsNotNone(result)

    @patch('local_vision.logic.image_processor.Image')
    def test_process_and_resize_failure(self, mock_pil_image):
        mock_pil_image.open.side_effect = Exception("File not found")
        
        result = ImageProcessor.process_and_resize("invalid.jpg")
        
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
