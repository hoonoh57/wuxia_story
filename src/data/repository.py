"""
Repository - Database CRUD abstraction

Provides high-level database operations for models.
All methods return detached-safe values (IDs, dicts) or
use expunge to safely return ORM objects outside session.
"""

import logging
from typing import Optional, List
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

from .models import Base, Project, Episode, Step, StepVersion, StepStatus

logger = logging.getLogger(__name__)


class Repository:
    """Database repository for CRUD operations"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self._SessionFactory = sessionmaker(bind=self.engine)
        logger.info(f"Repository initialized with database: {database_url}")

    def get_session(self) -> Session:
        """Get a new database session"""
        return self._SessionFactory()

    # -----------------------------------------
    # Project operations
    # -----------------------------------------

    def create_project(self, name: str, description: str = "") -> dict:
        """Create a new project. Returns dict with id and name."""
        session = self.get_session()
        try:
            project = Project(name=name, description=description)
            session.add(project)
            session.commit()
            result = {"id": project.id, "name": project.name}
            logger.info(f"Created project: {name} (id={result['id']})")
            return result
        finally:
            session.close()

    def get_project(self, project_id: int) -> Optional[dict]:
        """Get a project by ID. Returns dict or None."""
        session = self.get_session()
        try:
            project = session.query(Project).filter(Project.id == project_id).first()
            if project:
                return {"id": project.id, "name": project.name, "description": project.description}
            return None
        finally:
            session.close()

    # -----------------------------------------
    # Episode operations
    # -----------------------------------------

    def create_episode(self, project_id: int, episode_number: int, title: str = "") -> dict:
        """Create a new episode and auto-generate 6 steps. Returns dict with id."""
        session = self.get_session()
        try:
            episode = Episode(
                project_id=project_id,
                episode_number=episode_number,
                title=title,
            )
            session.add(episode)
            session.flush()

            step_names = [
                "material_selection",
                "world_design",
                "episode_structure",
                "scene_narration",
                "visual_prompts",
                "final_approval",
            ]

            for i, step_name in enumerate(step_names, 1):
                step = Step(
                    episode_id=episode.id,
                    step_number=i,
                    step_name=step_name,
                )
                session.add(step)

            session.commit()
            result = {"id": episode.id, "episode_number": episode_number, "title": title}
            logger.info(f"Created episode {episode_number} with 6 steps (id={result['id']})")
            return result
        finally:
            session.close()

    # -----------------------------------------
    # StepVersion operations
    # -----------------------------------------

    def create_step_version(
        self,
        step_id: int,
        content: str,
        status: StepStatus = StepStatus.DRAFT,
        ai_generated: bool = False,
        created_by: str = "",
    ) -> dict:
        """
        Create a new step version. Returns dict with id and version_number.
        """
        session = self.get_session()
        try:
            last_version = (
                session.query(StepVersion)
                .filter(StepVersion.step_id == step_id)
                .order_by(StepVersion.version_number.desc())
                .first()
            )
            version_number = (last_version.version_number + 1) if last_version else 1

            version = StepVersion(
                step_id=step_id,
                version_number=version_number,
                status=status,
                content=content,
                ai_generated=ai_generated,
                created_by=created_by,
            )
            session.add(version)
            session.commit()

            result = {"id": version.id, "version_number": version_number}
            logger.info(f"Created StepVersion v{version_number} for step {step_id} (id={result['id']})")
            return result
        finally:
            session.close()

    def get_approved_step_version(self, step_id: int) -> Optional[dict]:
        """
        Get the approved version of a step. Returns dict or None.
        """
        session = self.get_session()
        try:
            version = (
                session.query(StepVersion)
                .filter(
                    StepVersion.step_id == step_id,
                    StepVersion.status == StepStatus.APPROVED,
                )
                .first()
            )
            if version:
                return {
                    "id": version.id,
                    "version_number": version.version_number,
                    "content": version.content,
                    "created_by": version.created_by,
                    "ai_generated": version.ai_generated,
                    "status": version.status.value,
                }
            return None
        finally:
            session.close()

    def approve_step_version(self, version_id: int) -> bool:
        """Approve a step version. Returns True on success."""
        session = self.get_session()
        try:
            version = session.query(StepVersion).filter(StepVersion.id == version_id).first()
            if version:
                version.status = StepStatus.APPROVED
                session.commit()
                logger.info(f"Approved StepVersion {version_id}")
                return True
            logger.warning(f"StepVersion {version_id} not found")
            return False
        finally:
            session.close()
