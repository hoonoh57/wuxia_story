"""
History Viewer - Version history and change tracking interface

Placeholder for future detailed version comparison.
Basic history is available via the Step Editor's History button.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class HistoryViewer(QWidget):
    """History viewer widget"""

    def __init__(self, repository=None):
        super().__init__()
        self.repository = repository
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Version History Viewer")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(title)

        info = QLabel(
            "Basic version history is available via the Step Editor.\n"
            "Future: Side-by-side diff, rollback, timeline view."
        )
        info.setStyleSheet("padding: 8px; color: #888;")
        layout.addWidget(info)

        self.setLayout(layout)
