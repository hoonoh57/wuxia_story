"""
Skill Loader - Compiles markdown skill files into system prompts

Reads docs/SKILL_FILES/*.md and assembles them into complete system prompts
for each agent. The MASTER_SYSTEM prompt is prepended to all agent prompts.

Single source of truth: only markdown files are edited, code reads them.
"""

import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Mapping: agent name → skill file name
SKILL_FILE_MAP = {
    "master": "MASTER_SYSTEM_v3.0.md",
    "narrator": "SK-01_NARRATOR.md",
    "story": "SK-02_STORY.md",
    "prompt": "SK-03_PROMPT.md",
    "material": "SK-04_MATERIAL.md",
}

# Mapping: pipeline step → which agent skills to combine
STEP_AGENT_MAP = {
    "material_selection": ["material"],
    "world_design": ["narrator", "story"],
    "episode_structure": ["story"],
    "scene_narration": ["narrator"],
    "visual_prompts": ["prompt"],
    "final_approval": [],
}


class SkillLoader:
    """Loads and compiles skill markdown files into system prompts"""

    def __init__(self, skill_dir: Optional[Path] = None):
        """
        Initialize Skill Loader.

        Args:
            skill_dir: Path to skill files directory.
                       Defaults to <project_root>/docs/SKILL_FILES
        """
        if skill_dir is None:
            skill_dir = Path(__file__).parent.parent.parent / "docs" / "SKILL_FILES"

        self.skill_dir = Path(skill_dir)
        self._cache: Dict[str, str] = {}
        self._loaded = False

    def load_all(self) -> Dict[str, str]:
        """
        Load all skill files from disk into cache.

        Returns:
            Dictionary mapping skill names to their raw markdown content
        """
        self._cache.clear()

        if not self.skill_dir.exists():
            logger.error(f"Skill directory not found: {self.skill_dir}")
            return self._cache

        for skill_name, filename in SKILL_FILE_MAP.items():
            filepath = self.skill_dir / filename
            if filepath.exists():
                content = filepath.read_text(encoding="utf-8").strip()
                self._cache[skill_name] = content
                logger.info(f"Loaded skill: {skill_name} ({len(content)} chars)")
            else:
                logger.warning(f"Skill file not found: {filepath}")

        self._loaded = True
        logger.info(f"All skills loaded: {len(self._cache)}/{len(SKILL_FILE_MAP)}")
        return self._cache

    def get_raw(self, skill_name: str) -> str:
        """
        Get raw markdown content for a skill.

        Args:
            skill_name: Skill identifier (master, narrator, story, prompt, material)

        Returns:
            Raw markdown string, or empty string if not found
        """
        if not self._loaded:
            self.load_all()

        content = self._cache.get(skill_name, "")
        if not content:
            logger.warning(f"Skill not found in cache: {skill_name}")
        return content

    def build_system_prompt(self, agent_name: str) -> str:
        """
        Build a complete system prompt for a specific agent.

        Combines MASTER_SYSTEM + agent-specific skill file.

        Args:
            agent_name: Agent identifier (narrator, story, prompt, material)

        Returns:
            Complete system prompt string
        """
        if not self._loaded:
            self.load_all()

        parts = []

        # Always include master system prompt
        master = self._cache.get("master", "")
        if master:
            parts.append(master)

        # Add agent-specific skill
        agent_skill = self._cache.get(agent_name, "")
        if agent_skill:
            parts.append(agent_skill)
        else:
            logger.warning(f"No skill file found for agent: {agent_name}")

        prompt = "\n\n---\n\n".join(parts)
        logger.debug(
            f"Built system prompt for {agent_name}: {len(prompt)} chars"
        )
        return prompt

    def build_step_prompt(self, step_name: str) -> str:
        """
        Build a combined system prompt for a pipeline step.

        Some steps use multiple agents (e.g., world_design uses narrator + story).

        Args:
            step_name: Pipeline step name (e.g., 'world_design')

        Returns:
            Combined system prompt string
        """
        if not self._loaded:
            self.load_all()

        agent_names = STEP_AGENT_MAP.get(step_name, [])

        if not agent_names:
            logger.info(f"Step '{step_name}' has no agent skills (human-only step)")
            return self._cache.get("master", "")

        parts = []

        # Always include master
        master = self._cache.get("master", "")
        if master:
            parts.append(master)

        # Add each agent's skill
        for agent_name in agent_names:
            agent_skill = self._cache.get(agent_name, "")
            if agent_skill:
                parts.append(agent_skill)

        prompt = "\n\n---\n\n".join(parts)
        logger.debug(
            f"Built step prompt for {step_name} "
            f"(agents: {agent_names}): {len(prompt)} chars"
        )
        return prompt

    def reload(self):
        """Force reload all skill files from disk."""
        logger.info("Reloading all skill files...")
        self._loaded = False
        self.load_all()

    def get_loaded_skills(self) -> Dict[str, int]:
        """
        Get summary of loaded skills.

        Returns:
            Dictionary mapping skill names to their content length
        """
        if not self._loaded:
            self.load_all()
        return {name: len(content) for name, content in self._cache.items()}
