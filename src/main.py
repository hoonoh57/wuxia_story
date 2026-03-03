"""
Main entry point for Wuxia Story application
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from core.config_loader import load_config
from ui.main_window import MainWindow


def setup_logging(config):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.get('logging', {}).get('level', 'INFO')),
        format=config.get('logging', {}).get('format', '[%(asctime)s] %(levelname)s - %(name)s: %(message)s')
    )


def main():
    """Main application entry point"""
    try:
        # Load configuration
        config = load_config()
        setup_logging(config)
        
        logger = logging.getLogger(__name__)
        logger.info("Starting Wuxia Story Application")
        
        # Initialize UI
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        
        # Create and show main window
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
        
    except Exception as e:
        logging.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
