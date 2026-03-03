"""
Main application window - PySide6 UI

Central hub connecting all components:
- Left panel: Project/Episode/Step tree navigator
- Center panel: StepEditor (core editing area)
- Bottom: Status bar with mode indicator and Gemini status
"""

import logging

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QPushButton, QLabel, QMenuBar,
    QStatusBar, QMessageBox, QInputDialog, QComboBox, QToolBar,
)
from PySide6.QtCore import Qt

from src.ui.step_editor import StepEditor
from src.core.pipeline import STEP_DEFINITIONS

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(
        self, config, repository, gemini_client,
        skill_loader, dispatcher, pipeline,
    ):
        super().__init__()
        self.config = config
        self.repository = repository
        self.gemini_client = gemini_client
        self.skill_loader = skill_loader
        self.dispatcher = dispatcher
        self.pipeline = pipeline

        self._current_episode_id = None
        self._current_step = None

        self.init_ui()
        self.refresh_project_tree()

    def init_ui(self):
        """Initialize UI components"""
        ui = self.config.get("ui", {})
        self.setWindowTitle("Wuxia Story Studio v1.0.0")
        self.setGeometry(
            100, 100,
            ui.get("window_width", 1600),
            ui.get("window_height", 900),
        )

        # -- Menu bar --
        self._build_menu()

        # -- Toolbar --
        self._build_toolbar()

        # -- Central layout: splitter --
        splitter = QSplitter(Qt.Horizontal)

        # Left: project tree
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Project / Episode / Step"])
        self.project_tree.setMinimumWidth(280)
        self.project_tree.itemClicked.connect(self.on_tree_item_clicked)
        splitter.addWidget(self.project_tree)

        # Center: step editor
        self.step_editor = StepEditor(
            dispatcher=self.dispatcher,
            pipeline=self.pipeline,
            repository=self.repository,
        )
        splitter.addWidget(self.step_editor)

        splitter.setSizes([300, 1300])
        self.setCentralWidget(splitter)

        # -- Status bar --
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()

    # -----------------------------------------
    # Menu
    # -----------------------------------------

    def _build_menu(self):
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("New Project", self.on_new_project)
        file_menu.addAction("New Episode", self.on_new_episode)
        file_menu.addSeparator()
        file_menu.addAction("Refresh", self.refresh_project_tree)
        file_menu.addSeparator()
        file_menu.addAction("Exit", self.close)

        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        tools_menu.addAction("Gemini Usage", self.on_show_usage)
        tools_menu.addAction("Reload Skills", self.on_reload_skills)

    # -----------------------------------------
    # Toolbar
    # -----------------------------------------

    def _build_toolbar(self):
        toolbar = QToolBar("Mode")
        self.addToolBar(toolbar)

        toolbar.addWidget(QLabel("  Mode: "))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "A - Human Relay",
            "B - Gemini Auto",
            "C - Mixed (Recommended)",
        ])
        self.mode_combo.setCurrentIndex(2)  # Default: C
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        toolbar.addWidget(self.mode_combo)

        toolbar.addSeparator()
        self.bulk_btn = QPushButton("  FULL GENERATE  ")
        self.bulk_btn.setStyleSheet(
            "padding: 8px 24px; font-weight: bold; "
            "background-color: #1a6fd4; color: white; "
            "border-radius: 4px; font-size: 13px;"
        )
        self.bulk_btn.clicked.connect(self.on_bulk_generate)
        toolbar.addWidget(self.bulk_btn)

    # -----------------------------------------
    # Project tree
    # -----------------------------------------

    def refresh_project_tree(self):
        """Reload project tree from database"""
        self.project_tree.clear()
        session = self.repository.get_session()
        try:
            from src.data.models import Project, Episode, Step
            projects = session.query(Project).all()

            for project in projects:
                proj_item = QTreeWidgetItem([f"[P] {project.name}"])
                proj_item.setData(0, Qt.UserRole, {"type": "project", "id": project.id})

                episodes = session.query(Episode).filter(
                    Episode.project_id == project.id
                ).order_by(Episode.episode_number).all()

                for episode in episodes:
                    ep_label = f"[EP{episode.episode_number:02d}]"
                    if episode.title:
                        ep_label += f" {episode.title}"
                    ep_item = QTreeWidgetItem([ep_label])
                    ep_item.setData(0, Qt.UserRole, {"type": "episode", "id": episode.id})

                    steps = session.query(Step).filter(
                        Step.episode_id == episode.id
                    ).order_by(Step.step_number).all()

                    for step in steps:
                        approved = self.repository.get_approved_step_version(step.id)
                        status_mark = "[OK]" if approved else "[  ]"
                        step_def = STEP_DEFINITIONS[step.step_number - 1]
                        step_label = f"{status_mark} {step_def['label']}"
                        step_item = QTreeWidgetItem([step_label])
                        step_item.setData(0, Qt.UserRole, {
                            "type": "step",
                            "id": step.id,
                            "episode_id": episode.id,
                            "step_number": step.step_number,
                            "step_name": step.step_name,
                        })
                        ep_item.addChild(step_item)

                    proj_item.addChild(ep_item)

                self.project_tree.addTopLevelItem(proj_item)

            self.project_tree.expandAll()
        finally:
            session.close()

    def on_tree_item_clicked(self, item, column):
        """Handle tree item click"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return

        if data["type"] == "step":
            self._current_episode_id = data["episode_id"]
            self._current_step = data
            self.step_editor.load_step(
                step_id=data["id"],
                step_number=data["step_number"],
                step_name=data["step_name"],
                episode_id=data["episode_id"],
            )

    # -----------------------------------------
    # Actions
    # -----------------------------------------

    def on_new_project(self):
        name, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and name.strip():
            self.repository.create_project(name.strip())
            self.refresh_project_tree()
            self.status_bar.showMessage(f"Project '{name}' created", 3000)

    def on_new_episode(self):
        if not self._get_first_project_id():
            QMessageBox.warning(self, "Warning", "Create a project first.")
            return

        project_id = self._get_first_project_id()
        title, ok = QInputDialog.getText(self, "New Episode", "Episode title:")
        if ok:
            # Get next episode number
            session = self.repository.get_session()
            try:
                from src.data.models import Episode
                max_ep = session.query(Episode).filter(
                    Episode.project_id == project_id
                ).order_by(Episode.episode_number.desc()).first()
                next_num = (max_ep.episode_number + 1) if max_ep else 1
            finally:
                session.close()

            self.repository.create_episode(project_id, next_num, title.strip())
            self.refresh_project_tree()
            self.status_bar.showMessage(
                f"EP{next_num:02d} '{title}' created (6 steps auto-generated)", 3000
            )

    def on_mode_changed(self, index):
        modes = ["A", "B", "C"]
        self.dispatcher.set_mode(modes[index])
        self._update_status_bar()

    def on_show_usage(self):
        if self.gemini_client:
            stats = self.gemini_client.get_usage_stats()
            msg = (
                f"Total requests: {stats['total_requests']}\n"
                f"Input tokens: {stats['total_input_tokens']:,}\n"
                f"Output tokens: {stats['total_output_tokens']:,}\n"
                f"Errors: {stats['total_errors']}\n"
                f"Current key: #{stats['current_key_index']}"
            )
            QMessageBox.information(self, "Gemini Usage", msg)
        else:
            QMessageBox.information(self, "Gemini Usage", "Gemini client not connected")

    def on_reload_skills(self):
        self.skill_loader.reload()
        self.status_bar.showMessage("Skill files reloaded", 3000)

    def on_bulk_generate(self):
        """One-shot full pipeline generation"""
        from PySide6.QtWidgets import QInputDialog, QProgressDialog, QApplication
        from src.core.bulk_generator import BulkGenerator

        # 1. Get or create project
        project_id = self._get_first_project_id()
        if not project_id:
            name, ok = QInputDialog.getText(
                self, "New Project", "Project name:"
            )
            if not ok or not name.strip():
                return
            result = self.repository.create_project(name.strip())
            project_id = result["id"]

        # 2. Get concept from user
        concept, ok = QInputDialog.getMultiLineText(
            self,
            "Full Generate",
            "Enter your story concept:\n"
            "(Can be one sentence or detailed description)\n\n"
            "Example: A servant boy discovers a forbidden martial art\n"
            "that was sealed by the orthodox sect, and rises to\n"
            "challenge the hypocritical power structure.",
            "",
        )
        if not ok or not concept.strip():
            return

        # 3. Create episode
        session = self.repository.get_session()
        try:
            from src.data.models import Episode
            max_ep = session.query(Episode).filter(
                Episode.project_id == project_id
            ).order_by(Episode.episode_number.desc()).first()
            next_num = (max_ep.episode_number + 1) if max_ep else 1
        finally:
            session.close()

        ep_result = self.repository.create_episode(
            project_id, next_num, concept[:50]
        )
        episode_id = ep_result["id"]

        # 4. Show progress
        progress = QProgressDialog(
            "Generating full pipeline...\n"
            "This may take 1-3 minutes.",
            "Cancel", 0, 0, self,
        )
        progress.setWindowTitle("Full Generate")
        progress.setMinimumDuration(0)
        progress.show()
        QApplication.processEvents()

        # 5. Run bulk generation
        bulk = BulkGenerator(
            gemini_client=self.gemini_client,
            skill_loader=self.skill_loader,
            repository=self.repository,
        )

        result = bulk.generate_full_pipeline(
            project_id=project_id,
            episode_id=episode_id,
            concept=concept,
        )

        progress.close()

        # 6. Show result
        if result["success"]:
            tokens = result.get("tokens_used", {})
            QMessageBox.information(
                self,
                "Complete",
                f"Full pipeline generated!\n\n"
                f"Tokens: {tokens.get('input', 0):,} in / "
                f"{tokens.get('output', 0):,} out\n\n"
                f"All 6 steps saved as drafts.\n"
                f"Click each step in the tree to review and edit.\n"
                f"Approve each step when satisfied.",
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Generation failed:\n{result.get('error', 'Unknown')}",
            )

        self.refresh_project_tree()

    # -----------------------------------------
    # Helpers
    # -----------------------------------------

    def _get_first_project_id(self):
        session = self.repository.get_session()
        try:
            from src.data.models import Project
            project = session.query(Project).first()
            return project.id if project else None
        finally:
            session.close()

    def _update_status_bar(self):
        mode = self.dispatcher.get_mode()
        mode_labels = {"A": "Human Relay", "B": "Gemini Auto", "C": "Mixed"}
        gemini_status = "Connected" if (self.gemini_client and self.gemini_client.is_available()) else "Not connected"
        self.status_bar.showMessage(
            f"Mode: {mode} ({mode_labels.get(mode, '?')})  |  "
            f"Gemini: {gemini_status}  |  "
            f"Skills: {len(self.skill_loader.get_loaded_skills())} loaded"
        )
