"""
Step Editor - Core UI for step-by-step story editing

Layout:
- Top: Step info header (step name, status, mode)
- Middle-left: Input area (user prompt / human content)
- Middle-right: Output area (AI result / approved content, read-only)
- Bottom: Action buttons (Submit, Save Edit, Approve, History)
"""

import json
import logging

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QPlainTextEdit, QGroupBox, QComboBox, QMessageBox, QSplitter,
)
from PySide6.QtCore import Qt

from src.core.pipeline import STEP_DEFINITIONS

logger = logging.getLogger(__name__)


class StepEditor(QWidget):
    """Step-by-step editor widget"""

    def __init__(self, dispatcher, pipeline, repository):
        super().__init__()
        self.dispatcher = dispatcher
        self.pipeline = pipeline
        self.repository = repository

        self._step_id = None
        self._step_number = None
        self._step_name = None
        self._episode_id = None
        self._last_version_id = None

        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()

        # -- Header --
        self.header_label = QLabel("Select a step from the project tree")
        self.header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 8px;")
        layout.addWidget(self.header_label)

        self.info_label = QLabel("")
        self.info_label.setStyleSheet("color: #888; padding: 0 8px 8px 8px;")
        layout.addWidget(self.info_label)

        # -- Splitter: Input / Output --
        splitter = QSplitter(Qt.Horizontal)

        # Left: Input area
        input_group = QGroupBox("Input (Prompt / Human Content)")
        input_layout = QVBoxLayout()
        self.input_text = QPlainTextEdit()
        self.input_text.setPlaceholderText(
            "Mode A: Paste your content here\n"
            "Mode B/C: Enter a prompt for Gemini\n\n"
            "Example: Create a material brief for a story about "
            "a fallen martial arts master seeking redemption..."
        )
        input_layout.addWidget(self.input_text)
        input_group.setLayout(input_layout)
        splitter.addWidget(input_group)

        # Right: Output area (read-only)
        output_group = QGroupBox("Output (AI Result / Approved Content)")
        output_layout = QVBoxLayout()
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("Result will appear here after submission...")
        output_layout.addWidget(self.output_text)
        output_group.setLayout(output_layout)
        splitter.addWidget(output_group)

        splitter.setSizes([600, 600])
        layout.addWidget(splitter)

        # -- Version info --
        self.version_label = QLabel("")
        self.version_label.setStyleSheet("color: #666; padding: 4px 8px;")
        layout.addWidget(self.version_label)

        # -- Action buttons --
        btn_layout = QHBoxLayout()

        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setStyleSheet("padding: 8px 20px; font-weight: bold;")
        self.submit_btn.clicked.connect(self.on_submit)
        self.submit_btn.setEnabled(False)
        btn_layout.addWidget(self.submit_btn)

        self.edit_btn = QPushButton("Save Edit")
        self.edit_btn.setStyleSheet("padding: 8px 20px;")
        self.edit_btn.clicked.connect(self.on_save_edit)
        self.edit_btn.setEnabled(False)
        btn_layout.addWidget(self.edit_btn)

        self.approve_btn = QPushButton("Approve")
        self.approve_btn.setStyleSheet(
            "padding: 8px 20px; font-weight: bold; "
            "background-color: #2d7d2d; color: white;"
        )
        self.approve_btn.clicked.connect(self.on_approve)
        self.approve_btn.setEnabled(False)
        btn_layout.addWidget(self.approve_btn)

        self.history_btn = QPushButton("Version History")
        self.history_btn.setStyleSheet("padding: 8px 20px;")
        self.history_btn.clicked.connect(self.on_show_history)
        self.history_btn.setEnabled(False)
        btn_layout.addWidget(self.history_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    # -----------------------------------------
    # Load step
    # -----------------------------------------

    def load_step(self, step_id, step_number, step_name, episode_id):
        """
        Load a step into the editor.

        Args:
            step_id: Database Step ID
            step_number: Step number (1-6)
            step_name: Step name string
            episode_id: Parent episode ID
        """
        self._step_id = step_id
        self._step_number = step_number
        self._step_name = step_name
        self._episode_id = episode_id
        self._last_version_id = None

        step_def = STEP_DEFINITIONS[step_number - 1]

        # Update header
        self.header_label.setText(step_def["label"])
        self.info_label.setText(
            f"Step {step_number}/6  |  "
            f"Default mode: {step_def['default_mode']}  |  "
            f"{step_def['description']}"
        )

        # Clear fields
        self.input_text.clear()
        self.output_text.clear()

        # Load existing approved version if any
        approved = self.repository.get_approved_step_version(step_id)
        if approved:
            self.output_text.setPlainText(approved.content)
            self.version_label.setText(
                f"Approved: v{approved.version_number} "
                f"(by {approved.created_by})"
            )
        else:
            # Load latest draft if exists
            self._load_latest_draft(step_id)

        # Enable buttons
        self.submit_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.approve_btn.setEnabled(True)
        self.history_btn.setEnabled(True)

    def _load_latest_draft(self, step_id):
        """Load the latest draft version for display."""
        session = self.repository.get_session()
        try:
            from src.data.models import StepVersion
            latest = session.query(StepVersion).filter(
                StepVersion.step_id == step_id
            ).order_by(StepVersion.version_number.desc()).first()

            if latest:
                self.output_text.setPlainText(latest.content)
                self._last_version_id = latest.id
                self.version_label.setText(
                    f"Draft: v{latest.version_number} "
                    f"(by {latest.created_by}, {latest.status.value})"
                )
            else:
                self.version_label.setText("No versions yet")
        finally:
            session.close()

    # -----------------------------------------
    # Actions
    # -----------------------------------------

    def on_submit(self):
        """Submit: execute step via pipeline"""
        if not self._step_id:
            return

        user_input = self.input_text.toPlainText().strip()
        if not user_input:
            QMessageBox.warning(self, "Warning", "Please enter a prompt or content.")
            return

        # Execute via pipeline
        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("Processing...")

        try:
            result = self.pipeline.execute_step(
                episode_id=self._episode_id,
                step_number=self._step_number,
                user_prompt=user_input,
            )

            if result["success"]:
                self.output_text.setPlainText(result["content"])
                self._last_version_id = result.get("version_id")

                status = "DRAFT (needs review)" if result.get("needs_review") else "DRAFT"
                self.version_label.setText(
                    f"Generated: mode {result['mode']} | {status}"
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Step execution failed:\n{result.get('error', 'Unknown error')}"
                )

        except Exception as e:
            logger.error(f"Submit error: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Unexpected error:\n{str(e)}")
        finally:
            self.submit_btn.setEnabled(True)
            self.submit_btn.setText("Submit")

    def on_save_edit(self):
        """Save the current output text as a human edit."""
        if not self._step_id:
            return

        content = self.output_text.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Warning", "Output area is empty.")
            return

        result = self.pipeline.save_edit(self._step_id, content)

        if result["success"]:
            self._last_version_id = result.get("version_id")
            self.version_label.setText("Human edit saved as new draft")
        else:
            QMessageBox.critical(self, "Error", "Failed to save edit.")

    def on_approve(self):
        """Approve the current version."""
        if not self._last_version_id:
            QMessageBox.warning(
                self, "Warning",
                "No version to approve. Submit or save an edit first."
            )
            return

        reply = QMessageBox.question(
            self, "Confirm Approval",
            "Approve this version?\n\n"
            "This will make it the official output for this step, "
            "and unlock the next step.",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            result = self.pipeline.approve_step(self._last_version_id)
            if result["success"]:
                self.version_label.setText("APPROVED")
                QMessageBox.information(
                    self, "Approved",
                    "Step approved. You can now proceed to the next step."
                )
                # Notify parent to refresh tree
                parent = self.parent()
                while parent:
                    if hasattr(parent, "refresh_project_tree"):
                        parent.refresh_project_tree()
                        break
                    parent = parent.parent()

    def on_show_history(self):
        """Show version history for current step."""
        if not self._step_id:
            return

        session = self.repository.get_session()
        try:
            from src.data.models import StepVersion
            versions = session.query(StepVersion).filter(
                StepVersion.step_id == self._step_id
            ).order_by(StepVersion.version_number.desc()).all()

            if not versions:
                QMessageBox.information(self, "History", "No versions yet.")
                return

            lines = []
            for v in versions:
                status = v.status.value.upper()
                ai_tag = " [AI]" if v.ai_generated else ""
                lines.append(
                    f"v{v.version_number} | {status} | {v.created_by}{ai_tag} | "
                    f"{v.created_at.strftime('%Y-%m-%d %H:%M') if v.created_at else 'N/A'}"
                )

            QMessageBox.information(
                self, "Version History",
                f"Step: {self._step_name}\n\n" + "\n".join(lines)
            )
        finally:
            session.close()
