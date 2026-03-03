"""
Step Editor - Core UI for step-by-step story editing

Provides interface for:
- Executing steps via dispatcher
- Editing AI-generated content
- Approving and moving to next step
- Viewing version history
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class StepEditor(QWidget):
    """Step-by-step editor widget"""
    
    def __init__(self, dispatcher, episode):
        """
        Initialize Step Editor
        
        Args:
            dispatcher: Dispatcher for step execution
            episode: Episode to edit
        """
        super().__init__()
        self.dispatcher = dispatcher
        self.episode = episode
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Step Editor - Coming Soon"))
        self.setLayout(layout)
        # TODO: Implement full step editor UI
