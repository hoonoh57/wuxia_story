"""
SQLAlchemy data models for Wuxia Story

Models:
- Project: Top-level project
- Episode: Story episode within a project
- Step: Pipeline step within an episode (6 steps per episode)
- StepVersion: Version history for steps (draft/approved)
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class StepStatus(enum.Enum):
    """Step status enumeration"""
    DRAFT = "draft"
    APPROVED = "approved"


class Project(Base):
    """Project model - top-level container"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    episodes = relationship("Episode", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class Episode(Base):
    """Episode model - story episodes within a project"""
    __tablename__ = "episodes"
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    episode_number = Column(Integer)
    title = Column(String(255))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="episodes")
    steps = relationship("Step", back_populates="episode", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Episode(id={self.id}, episode_number={self.episode_number}, title='{self.title}')>"


class Step(Base):
    """Step model - pipeline steps within an episode (6 steps per episode)"""
    __tablename__ = "steps"
    
    id = Column(Integer, primary_key=True)
    episode_id = Column(Integer, ForeignKey("episodes.id"), nullable=False)
    step_number = Column(Integer)  # 1-6
    step_name = Column(String(100))  # material_selection, world_design, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    episode = relationship("Episode", back_populates="steps")
    versions = relationship("StepVersion", back_populates="step", cascade="all, delete-orphan")
    
    def get_approved_version(self):
        """Get the approved version of this step"""
        for version in self.versions:
            if version.status == StepStatus.APPROVED:
                return version
        return None
    
    def __repr__(self):
        return f"<Step(id={self.id}, step_number={self.step_number}, step_name='{self.step_name}')>"


class StepVersion(Base):
    """StepVersion model - version history for steps"""
    __tablename__ = "step_versions"
    
    id = Column(Integer, primary_key=True)
    step_id = Column(Integer, ForeignKey("steps.id"), nullable=False)
    version_number = Column(Integer)
    status = Column(Enum(StepStatus), default=StepStatus.DRAFT)
    content = Column(Text, nullable=False)  # JSON content
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(50))  # "gemini_auto", "human_edit", etc.
    
    step = relationship("Step", back_populates="versions")
    
    def __repr__(self):
        return f"<StepVersion(id={self.id}, step_id={self.step_id}, version={self.version_number}, status={self.status.value})>"
