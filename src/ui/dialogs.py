"""
Common dialogs for the application
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QFormLayout,
)


class NewProjectDialog(QDialog):
    """New project creation dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Project")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter project name")
        form.addRow("Name:", self.name_input)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Optional description")
        form.addRow("Description:", self.desc_input)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_values(self):
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip(),
        }


class NewEpisodeDialog(QDialog):
    """New episode creation dialog"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Episode")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter episode title")
        form.addRow("Title:", self.title_input)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Create")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_values(self):
        return {
            "title": self.title_input.text().strip(),
        }
