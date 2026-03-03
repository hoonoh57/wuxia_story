"""
Main application window - PySide6 UI
"""

from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI components"""
        self.setWindowTitle("Wuxia Story - AI Multi-Agent Story Generation")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout()
        
        # Add title
        title = QLabel("Wuxia Story Generation System")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(title)
        
        # Add buttons layout
        button_layout = QHBoxLayout()
        
        new_project_btn = QPushButton("New Project")
        new_project_btn.clicked.connect(self.on_new_project)
        button_layout.addWidget(new_project_btn)
        
        open_project_btn = QPushButton("Open Project")
        open_project_btn.clicked.connect(self.on_open_project)
        button_layout.addWidget(open_project_btn)
        
        main_layout.addLayout(button_layout)
        
        # Set central widget layout
        central_widget.setLayout(main_layout)
    
    def on_new_project(self):
        """Handle new project button click"""
        print("New project clicked")
        # TODO: Implement new project dialog
    
    def on_open_project(self):
        """Handle open project button click"""
        print("Open project clicked")
        # TODO: Implement open project dialog
