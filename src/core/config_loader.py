"""
Configuration loader - reads config.yaml and environment variables

Handles:
- YAML config loading
- Environment variable overrides
- Multiple Gemini API key management
- Path resolution
"""

import logging
import os
from pathlib import Path
from typing import List

import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


def load_config() -> dict:
    """
    Load configuration from YAML file and environment variables.

    Environment variables override YAML settings.
    API keys are loaded exclusively from .env (never from YAML).

    Returns:
        Configuration dictionary
    """
    # Load environment variables from .env file
    env_path = PROJECT_ROOT / ".env"
    load_dotenv(env_path)

    # Load YAML configuration
    config_path = PROJECT_ROOT / "config.yaml"

    if not config_path.exists():
        logger.warning(f"Config file not found at {config_path}, using defaults")
        config = _default_config()
    else:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

    # Inject API keys from environment
    config["gemini"] = config.get("gemini", {})
    config["gemini"]["api_keys"] = _load_api_keys()
    config["gemini"]["model"] = os.getenv(
        "GEMINI_MODEL",
        config["gemini"].get("model", "gemini-2.5-flash")
    )

    # Resolve database path
    db_relative = config.get("project", {}).get("database", "projects/wuxia.db")
    config["database_url"] = f"sqlite:///{PROJECT_ROOT / db_relative}"

    # Resolve skill files directory
    skill_dir = config.get("skill_files", {}).get("directory", "docs/SKILL_FILES")
    config["skill_files_path"] = PROJECT_ROOT / skill_dir

    # Store project root for reference
    config["project_root"] = str(PROJECT_ROOT)

    # Auto-approve threshold
    config["auto_approve_threshold"] = float(
        os.getenv(
            "AUTO_APPROVE_THRESHOLD",
            config.get("pipeline", {}).get("auto_approve_threshold", 0.7)
        )
    )

    logger.info("Configuration loaded successfully")
    logger.info(f"  API keys: {len(config['gemini']['api_keys'])} loaded")
    logger.info(f"  Model: {config['gemini']['model']}")
    logger.info(f"  Database: {config['database_url']}")

    return config


def _load_api_keys() -> List[str]:
    """
    Load Gemini API keys from environment variables.

    Reads GEMINI_API_KEY_1, GEMINI_API_KEY_2, GEMINI_API_KEY_3.
    Falls back to GEMINI_API_KEY if numbered keys not found.

    Returns:
        List of valid API key strings
    """
    keys = []

    # Try numbered keys first
    for i in range(1, 4):
        key = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
        if key and key != "your-api-key-here":
            keys.append(key)

    # Fallback to single key
    if not keys:
        single_key = os.getenv("GEMINI_API_KEY", "").strip()
        if single_key and single_key != "your-api-key-here":
            keys.append(single_key)

    if not keys:
        logger.warning("No Gemini API keys found in environment variables!")

    return keys


def _default_config() -> dict:
    """Return default configuration"""
    return {
        "project": {
            "name": "무림 스토리 스튜디오",
            "version": "1.0.0",
            "database": "projects/wuxia.db",
        },
        "gemini": {
            "model": "gemini-2.5-flash",
            "max_tokens": 8000,
            "temperature": 0.8,
            "key_rotation": True,
            "retry_count": 3,
            "retry_delay": 2,
        },
        "pipeline": {
            "steps": [
                "STEP1_MATERIAL",
                "STEP2_WORLDBUILD",
                "STEP3_STRUCTURE",
                "STEP4_NARRATIVE",
                "STEP5_PROMPT",
                "STEP6_APPROVAL",
            ],
            "auto_approve_threshold": 0.7,
        },
        "ui": {
            "theme": "dark",
            "window_width": 1600,
            "window_height": 900,
            "font_size": 11,
        },
        "skill_files": {
            "directory": "docs/SKILL_FILES",
            "master": "MASTER_SYSTEM_v3.0.md",
            "narrator": "SK-01_NARRATOR.md",
            "story": "SK-02_STORY.md",
            "prompt": "SK-03_PROMPT.md",
            "material": "SK-04_MATERIAL.md",
        },
    }
