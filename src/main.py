"""
Main entry point for Wuxia Story application

Initializes all components and launches the UI:
1. Load configuration
2. Initialize database (Repository)
3. Initialize Gemini client
4. Initialize Skill Loader
5. Initialize Dispatcher
6. Initialize Pipeline
7. Launch PySide6 UI
"""

import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Starting Wuxia Story Studio v1.0.0")
    logger.info("=" * 50)

    try:
        # 1. Load configuration
        from src.core.config_loader import load_config

        config = load_config()

        # 2. Initialize database
        from src.data.repository import Repository

        repository = Repository(config["database_url"])
        logger.info("Database initialized")

        # 3. Initialize Gemini client
        from src.core.gemini_client import GeminiClient

        gemini_client = None
        api_keys = config.get("gemini", {}).get("api_keys", [])
        if api_keys:
            gemini_client = GeminiClient(
                api_keys=api_keys,
                model=config["gemini"].get("model", "gemini-2.5-flash"),
                max_tokens=config["gemini"].get("max_tokens", 8000),
                temperature=config["gemini"].get("temperature", 0.8),
                max_retries=config["gemini"].get("retry_count", 3),
                retry_delay=config["gemini"].get("retry_delay", 2.0),
            )
            logger.info("Gemini client initialized")
        else:
            logger.warning("No API keys found — running in human-relay mode only")

        # 4. Initialize Skill Loader
        from src.core.skill_loader import SkillLoader

        skill_loader = SkillLoader(config.get("skill_files_path"))
        skill_loader.load_all()
        logger.info(f"Skills loaded: {skill_loader.get_loaded_skills()}")

        # 5. Initialize Dispatcher
        from src.core.dispatcher import Dispatcher

        dispatcher = Dispatcher(
            gemini_client=gemini_client,
            skill_loader=skill_loader,
            repository=repository,
        )
        logger.info("Dispatcher initialized")

        # 6. Initialize Pipeline
        from src.core.pipeline import Pipeline

        pipeline = Pipeline(
            dispatcher=dispatcher,
            repository=repository,
        )
        logger.info("Pipeline initialized")

        # 7. Launch UI
        from PySide6.QtWidgets import QApplication

        app = QApplication(sys.argv)

        from src.ui.main_window import MainWindow

        window = MainWindow(
            config=config,
            repository=repository,
            gemini_client=gemini_client,
            skill_loader=skill_loader,
            dispatcher=dispatcher,
            pipeline=pipeline,
        )
        window.show()

        logger.info("UI launched — ready to use")
        sys.exit(app.exec())

    except Exception as e:
        logging.error(f"Application startup error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
