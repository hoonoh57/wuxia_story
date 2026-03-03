"""
Tests for Gemini Client
"""

import unittest
from src.core.gemini_client import GeminiClient


class TestGeminiClient(unittest.TestCase):
    """Gemini client test cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = GeminiClient("test-key", "gemini-2.0-flash")
    
    def test_client_initialization(self):
        """Test client initialization"""
        self.assertEqual(self.client.api_key, "test-key")
        self.assertEqual(self.client.model, "gemini-2.0-flash")
        self.assertEqual(self.client.max_retries, 3)


if __name__ == "__main__":
    unittest.main()
