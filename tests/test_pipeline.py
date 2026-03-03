"""
Tests for Pipeline
"""

import unittest
from src.core.pipeline import Pipeline


class TestPipeline(unittest.TestCase):
    """Pipeline test cases"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = Pipeline(None, None)
    
    def test_pipeline_steps(self):
        """Test pipeline step definitions"""
        expected_steps = [
            "material_selection",
            "world_design",
            "episode_structure",
            "scene_narration",
            "visual_prompts",
            "final_approval"
        ]
        self.assertEqual(self.pipeline.STEPS, expected_steps)


if __name__ == "__main__":
    unittest.main()
