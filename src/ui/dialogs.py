"""
Common dialogs for the application
"""

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class NewProjectDialog(QDialog):
    """New project dialog"""
    
    def __init__(self, parent=None):
        """Initialize new project dialog"""
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("New Project Dialog - Coming Soon"))
        self.setLayout(layout)
        # TODO: Implement new project dialog


class OpenProjectDialog(QDialog):
    """Open project dialog"""
    
    def __init__(self, parent=None):
        """Initialize open project dialog"""
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Open Project Dialog - Coming Soon"))
        self.setLayout(layout)
        # TODO: Implement open project dialog
