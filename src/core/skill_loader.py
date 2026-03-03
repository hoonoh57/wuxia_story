"""
Skill Loader - Compiles markdown skill files to system prompts

Reads docs/SKILL_FILES/*.md and converts to system prompts for agents
- MASTER_SYSTEM_v3.0.md: Base system prompt
- SK-01_NARRATOR.md: Narrator agent skill
- SK-02_STORY.md: Story agent skill
- SK-03_PROMPT.md: Prompt agent skill
- SK-04_MATERIAL.md: Material agent skill
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SkillLoader:
    """Loads and compiles skill markdown files to system prompts"""
    
    def __init__(self):
        """Initialize Skill Loader"""
        self.skill_dir = Path(__file__).parent.parent.parent / "docs" / "SKILL_FILES"
        self.skills = {}
    
    def load_all_skills(self) -> dict:
        """
        Load all skill files from docs/SKILL_FILES
        
        Returns:
            Dictionary mapping skill names to their content
        """
        logger.info("Loading skill files...")
        
        if not self.skill_dir.exists():
            logger.warning(f"Skill directory not found: {self.skill_dir}")
            return {}
        
        # TODO: Implement markdown loading and parsing
        
        return self.skills
    
    def get_system_prompt(self, skill_name: str) -> str:
        """
        Get system prompt for a specific skill
        
        Args:
            skill_name: Name of the skill (e.g., 'narrator', 'story')
            
        Returns:
            System prompt string
        """
        if skill_name not in self.skills:
            logger.warning(f"Skill not found: {skill_name}")
            return ""
        
        return self.skills[skill_name]
