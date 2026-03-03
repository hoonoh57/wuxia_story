"""
Tests for Agents
"""

import unittest
from src.agents import (
    MaterialAgent,
    NarratorAgent,
    StoryAgent,
    LanguageAgent,
    PromptAgent
)


class TestAgents(unittest.TestCase):
    """Agent test cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.material_agent = MaterialAgent(None)
        self.narrator_agent = NarratorAgent(None)
        self.story_agent = StoryAgent(None)
        self.language_agent = LanguageAgent(None)
        self.prompt_agent = PromptAgent(None)
    
    def test_agent_names(self):
        """Test agent names"""
        self.assertEqual(self.material_agent.name, "MaterialAgent")
        self.assertEqual(self.narrator_agent.name, "NarratorAgent")
        self.assertEqual(self.story_agent.name, "StoryAgent")
        self.assertEqual(self.language_agent.name, "LanguageAgent")
        self.assertEqual(self.prompt_agent.name, "PromptAgent")


if __name__ == "__main__":
    unittest.main()
