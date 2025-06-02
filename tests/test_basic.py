"""
Basic tests for the storyteller engine
"""

import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from storyteller_engine import StoryState, SymbolicValidator, StoryViolation

class TestStorytellerBasic(unittest.TestCase):

    def setUp(self):
        self.story_state = StoryState()
        self.validator = SymbolicValidator()

    def test_character_addition(self):
        self.story_state.add_character("Alice", status="alive")
        self.assertIn("Alice", self.story_state.characters)
        self.assertEqual(self.story_state.characters["Alice"].status, "alive")

    def test_death_violation_detection(self):
        test_story = "John died in the first chapter. Later, John said hello to Mary."
        self.story_state.add_character("John", status="dead")
        violations = self.validator.validate(test_story, self.story_state)
        death_violations = [v for v in violations if v.rule_name == "character_death"]
        self.assertTrue(len(death_violations) > 0)
        self.assertEqual(death_violations[0].severity, "high")

    def test_temporal_consistency(self):
        test_story = "It was morning when they started. In the evening, they continued from the morning."
        violations = self.validator.validate(test_story, self.story_state)
        temporal_violations = [v for v in violations if v.rule_name == "temporal_consistency"]
        self.assertTrue(len(temporal_violations) >= 1)

if __name__ == '__main__':
    unittest.main()
