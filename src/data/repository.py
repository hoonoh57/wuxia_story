"""
Repository - Database CRUD abstraction

Provides high-level database operations for models
"""

import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from .models import Base, Project, Episode, Step, StepVersion, StepStatus

logger = logging.getLogger(__name__)


class Repository:
    """Database repository for CRUD operations"""
    
    def __init__(self, database_url: str):
        """
        Initialize Repository
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        logger.info(f"Repository initialized with database: {database_url}")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=self.engine)
        return SessionLocal()
    
    # Project operations
    def create_project(self, name: str, description: str = "") -> Project:
        """Create a new project"""
        session = self.get_session()
        try:
            project = Project(name=name, description=description)
            session.add(project)
            session.commit()
            logger.info(f"Created project: {name}")
            return project
        finally:
            session.close()
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID"""
        session = self.get_session()
        try:
            return session.query(Project).filter(Project.id == project_id).first()
        finally:
            session.close()
    
    # Episode operations
    def create_episode(self, project_id: int, episode_number: int, title: str = "") -> Episode:
        """Create a new episode and auto-generate 6 steps"""
        session = self.get_session()
        try:
            episode = Episode(
                project_id=project_id,
                episode_number=episode_number,
                title=title
            )
            session.add(episode)
            session.flush()  # Flush to get the episode ID
            
            # Auto-generate 6 steps
            step_names = [
                "material_selection",
                "world_design",
                "episode_structure",
                "scene_narration",
                "visual_prompts",
                "final_approval"
            ]
            
            for i, step_name in enumerate(step_names, 1):
                step = Step(
                    episode_id=episode.id,
                    step_number=i,
                    step_name=step_name
                )
                session.add(step)
            
            session.commit()
            logger.info(f"Created episode {episode_number} with 6 steps")
            return episode
        finally:
            session.close()
    
    def get_episode(self, episode_id: int) -> Optional[Episode]:
        """Get an episode by ID"""
        session = self.get_session()
        try:
            return session.query(Episode).filter(Episode.id == episode_id).first()
        finally:
            session.close()
    
    # Step operations
    def get_step(self, step_id: int) -> Optional[Step]:
        """Get a step by ID"""
        session = self.get_session()
        try:
            return session.query(Step).filter(Step.id == step_id).first()
        finally:
            session.close()
    
    # StepVersion operations
    def create_step_version(self, step_id: int, content: str, status: StepStatus = StepStatus.DRAFT, 
                           ai_generated: bool = False, created_by: str = "") -> StepVersion:
        """Create a new step version"""
        session = self.get_session()
        try:
            # Get version number
            last_version = session.query(StepVersion).filter(
                StepVersion.step_id == step_id
            ).order_by(StepVersion.version_number.desc()).first()
            
            version_number = (last_version.version_number + 1) if last_version else 1
            
            version = StepVersion(
                step_id=step_id,
                version_number=version_number,
                status=status,
                content=content,
                ai_generated=ai_generated,
                created_by=created_by
            )
            session.add(version)
            session.commit()
            logger.info(f"Created StepVersion {version_number} for step {step_id}")
            return version
        finally:
            session.close()
    
    def get_approved_step_version(self, step_id: int) -> Optional[StepVersion]:
        """Get the approved version of a step"""
        session = self.get_session()
        try:
            return session.query(StepVersion).filter(
                StepVersion.step_id == step_id,
                StepVersion.status == StepStatus.APPROVED
            ).first()
        finally:
            session.close()
    
    def approve_step_version(self, version_id: int):
        """Approve a step version and set others to draft"""
        session = self.get_session()
        try:
            version = session.query(StepVersion).filter(StepVersion.id == version_id).first()
            if version:
                # Set this version to approved
                version.status = StepStatus.APPROVED
                session.commit()
                logger.info(f"Approved StepVersion {version_id}")
        finally:
            session.close()
