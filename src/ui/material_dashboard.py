"""
Material Dashboard - Material management and selection interface
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class MaterialDashboard(QWidget):
    """Material dashboard widget"""
    
    def __init__(self, repository):
        """
        Initialize Material Dashboard
        
        Args:
            repository: Database repository
        """
        super().__init__()
        self.repository = repository
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Material Dashboard - Coming Soon"))
        self.setLayout(layout)
        # TODO: Implement material dashboard UI
