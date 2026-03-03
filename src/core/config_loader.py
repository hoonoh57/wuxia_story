"""
Configuration loader - reads config.yaml and environment variables
"""

import logging
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_config() -> dict:
    """
    Load configuration from YAML file and environment variables
    
    Returns:
        Configuration dictionary
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Load YAML configuration
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    
    if not config_path.exists():
        logger.warning(f"Config file not found at {config_path}, using defaults")
        config = {}
    else:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
    
    # Override with environment variables
    config['gemini'] = config.get('gemini', {})
    config['gemini']['api_key'] = os.getenv('GEMINI_API_KEY', '')
    config['gemini']['model'] = os.getenv('GEMINI_MODEL', config['gemini'].get('model', 'gemini-2.0-flash'))
    
    config['database'] = config.get('database', {})
    config['database']['url'] = os.getenv('DATABASE_URL', config['database'].get('url', 'sqlite:///./projects/wuxia.db'))
    
    logger.info("Configuration loaded successfully")
    return config
