"""
Tests for Dispatcher
"""

import unittest
from src.core.dispatcher import Dispatcher, DispatchMode


class TestDispatcher(unittest.TestCase):
    """Dispatcher test cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.dispatcher = Dispatcher(None, "C")
    
    def test_dispatcher_initialization(self):
        """Test dispatcher initialization"""
        self.assertEqual(self.dispatcher.mode, DispatchMode.MIXED)
    
    def test_set_mode(self):
        """Test setting dispatcher mode"""
        self.dispatcher.set_mode("A")
        self.assertEqual(self.dispatcher.mode, DispatchMode.HUMAN_RELAY)
        
        self.dispatcher.set_mode("B")
        self.assertEqual(self.dispatcher.mode, DispatchMode.AUTO)
        
        self.dispatcher.set_mode("C")
        self.assertEqual(self.dispatcher.mode, DispatchMode.MIXED)


if __name__ == "__main__":
    unittest.main()
