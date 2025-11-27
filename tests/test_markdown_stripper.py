import unittest
import sys
import os
from unittest.mock import MagicMock

# Mock lmstudio before importing local_vision
sys.modules['lmstudio'] = MagicMock()

# Add the project root to the path so we can import local_vision
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from local_vision.logic.llm_manager import LLM_Manager

class TestMarkdownStripper(unittest.TestCase):
    def setUp(self):
        # We don't need a real connection for this test, so we can mock the client or just ignore the connection error if it happens during init
        # However, LLM_Manager init tries to connect. 
        # Let's subclass or mock to avoid connection
        class MockLLMManager(LLM_Manager):
            def __init__(self):
                pass # Skip init
        
        self.manager = MockLLMManager()

    def test_strip_bold(self):
        text = "This is **bold** text."
        expected = "This is bold text."
        self.assertEqual(self.manager._strip_markdown(text), expected)

    def test_strip_italic(self):
        text = "This is *italic* text."
        expected = "This is italic text."
        self.assertEqual(self.manager._strip_markdown(text), expected)

    def test_strip_code_block(self):
        text = "Here is code:\n```python\nprint('hello')\n```"
        expected = "Here is code:"
        self.assertEqual(self.manager._strip_markdown(text).strip(), expected)

    def test_strip_inline_code(self):
        text = "Use `print()` function."
        expected = "Use print() function."
        self.assertEqual(self.manager._strip_markdown(text), expected)

    def test_strip_headers(self):
        text = "# Header 1\n## Header 2\nContent"
        expected = "Header 1\nHeader 2\nContent"
        # The regex might leave newlines, let's check
        # My regex was: re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        # So "# Header 1" -> "Header 1"
        self.assertEqual(self.manager._strip_markdown(text), expected)

    def test_strip_links(self):
        text = "Check [Google](https://google.com) now."
        expected = "Check Google now."
        self.assertEqual(self.manager._strip_markdown(text), expected)

    def test_complex_mix(self):
        text = """
# Title
This is **bold** and *italic*.
Here is a list:
- Item 1
- Item 2

Code:
```
code
```
[Link](url)
"""
        # Note: My regex doesn't strip list bullets, which is fine as they are readable.
        # It should strip the header marker, bold/italic markers, code block, and link.
        expected_content = ["Title", "This is bold and italic.", "Here is a list:", "- Item 1", "- Item 2", "Code:", "Link"]
        
        result = self.manager._strip_markdown(text)
        for item in expected_content:
            self.assertIn(item, result)
        
        self.assertNotIn("**", result)
        self.assertNotIn("```", result)
        self.assertNotIn("](", result)

if __name__ == '__main__':
    unittest.main()
