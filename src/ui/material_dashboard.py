"""
Material Dashboard - Material management and selection interface

Placeholder for future material agent integration.
Currently shows basic info about the material pipeline.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPlainTextEdit,
)


class MaterialDashboard(QWidget):
    """Material dashboard widget"""

    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Material Dashboard")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(title)

        info = QLabel(
            "Use STEP 1 in the Step Editor to select materials.\n"
            "Future: TOP-10 pool, trend analysis, evaluation scoring."
        )
        info.setStyleSheet("padding: 8px; color: #888;")
        layout.addWidget(info)

        self.notes_area = QPlainTextEdit()
        self.notes_area.setPlaceholderText("Material notes and research...")
        layout.addWidget(self.notes_area)

        self.setLayout(layout)
