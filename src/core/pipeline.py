"""
Pipeline - 6-step story generation orchestrator

Manages the sequential workflow:
1. Material Selection → 2. World Design → 3. Episode Structure
→ 4. Scene Narration → 5. Visual Prompts → 6. Final Approval

Key responsibilities:
- Enforce step ordering (previous step must be approved)
- Auto-inject context from previous approved step
- Track pipeline status per episode
"""

import json
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


# Step definitions with metadata
STEP_DEFINITIONS = [
    {
        "number": 1,
        "name": "material_selection",
        "label": "STEP 1: 소재 선정",
        "default_mode": "A",
        "description": "소재 브리프 작성 (로그라인, 핵심 갈등, 타겟 독자, 심리 훅)",
    },
    {
        "number": 2,
        "name": "world_design",
        "label": "STEP 2: 세계관/캐릭터 설계",
        "default_mode": "C",
        "description": "세계관 설정서, 캐릭터 프로파일 (5층 레이어), 관계도",
    },
    {
        "number": 3,
        "name": "episode_structure",
        "label": "STEP 3: 에피소드 구조",
        "default_mode": "B",
        "description": "15비트 시퀀스, 씬 리스트, 타이밍 배분, 감정 곡선",
    },
    {
        "number": 4,
        "name": "scene_narration",
        "label": "STEP 4: 씬별 상세 서술",
        "default_mode": "C",
        "description": "각 씬의 내러티브 텍스트, 대사, 감정 지시, 액션 묘사",
    },
    {
        "number": 5,
        "name": "visual_prompts",
        "label": "STEP 5: 영상 프롬프트 변환",
        "default_mode": "B",
        "description": "씬별 이미지/비디오 생성 프롬프트, 카메라, 조명, 의상 지정",
    },
    {
        "number": 6,
        "name": "final_approval",
        "label": "STEP 6: 최종 패키지 승인",
        "default_mode": "A",
        "description": "영상 제작팀에 넘길 완성 패키지 최종 검수",
    },
]


class Pipeline:
    """Orchestrates the 6-step story generation pipeline"""

    STEPS = [s["name"] for s in STEP_DEFINITIONS]

    def __init__(self, dispatcher, repository):
        """
        Initialize Pipeline.

        Args:
            dispatcher: Dispatcher instance for mode management
            repository: Repository instance for DB operations
        """
        self.dispatcher = dispatcher
        self.repository = repository
        logger.info("Pipeline initialized with 6 steps")

    # ─────────────────────────────────────────────
    # Step execution
    # ─────────────────────────────────────────────

    def execute_step(
        self,
        episode_id: int,
        step_number: int,
        user_prompt: str,
        mode_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a specific pipeline step for an episode.

        Automatically:
        1. Validates that previous step is approved (if not step 1)
        2. Retrieves previous step's approved content as context
        3. Dispatches execution via the dispatcher
        4. Returns result

        Args:
            episode_id: Episode ID
            step_number: Step number (1-6)
            user_prompt: User's prompt or content
            mode_override: Override default mode for this step

        Returns:
            Result dictionary with status and content
        """
        if step_number < 1 or step_number > 6:
            return {"success": False, "error": f"Invalid step number: {step_number}"}

        step_def = STEP_DEFINITIONS[step_number - 1]
        step_name = step_def["name"]

        logger.info(f"Pipeline: executing {step_def['label']} for episode {episode_id}")

        # Get the Step record from DB
        step = self._get_step_record(episode_id, step_number)
        if not step:
            return {
                "success": False,
                "error": f"Step {step_number} not found for episode {episode_id}",
            }

        # Check prerequisite: previous step must be approved
        if step_number > 1:
            prev_ok, prev_error = self._check_previous_approved(episode_id, step_number)
            if not prev_ok:
                return {"success": False, "error": prev_error}

        # Get context from previous approved step
        context = self._get_previous_context(episode_id, step_number)

        # Determine mode
        mode = mode_override or step_def["default_mode"]

        # Dispatch
        result = self.dispatcher.execute_step(
            step_id=step.id,
            step_name=step_name,
            user_prompt=user_prompt,
            context=context,
            mode_override=mode,
        )

        return {
            "success": result.success,
            "content": result.content,
            "mode": result.mode,
            "needs_review": result.needs_review,
            "version_id": result.version_id,
            "error": result.error,
            "step_number": step_number,
            "step_name": step_name,
            "step_label": step_def["label"],
        }

    # ─────────────────────────────────────────────
    # Approval
    # ─────────────────────────────────────────────

    def approve_step(self, version_id: int) -> Dict[str, Any]:
        """
        Approve a step version.

        Args:
            version_id: StepVersion ID to approve

        Returns:
            Result dictionary
        """
        result = self.dispatcher.approve_version(version_id)
        return result.to_dict()

    def save_edit(self, step_id: int, content: str) -> Dict[str, Any]:
        """
        Save a human edit for a step.

        Args:
            step_id: Step ID
            content: Edited content

        Returns:
            Result dictionary
        """
        result = self.dispatcher.save_human_edit(step_id, content)
        return result.to_dict()

    # ─────────────────────────────────────────────
    # Status & info
    # ─────────────────────────────────────────────

    def get_episode_status(self, episode_id: int) -> List[Dict[str, Any]]:
        """
        Get the status of all 6 steps for an episode.

        Returns:
            List of step status dictionaries
        """
        status_list = []

        for step_def in STEP_DEFINITIONS:
            step = self._get_step_record(episode_id, step_def["number"])
            if not step:
                status_list.append({
                    "step_number": step_def["number"],
                    "step_name": step_def["name"],
                    "label": step_def["label"],
                    "status": "not_created",
                    "has_approved": False,
                    "version_count": 0,
                })
                continue

            approved = self.repository.get_approved_step_version(step.id)
            versions = step.versions if hasattr(step, "versions") else []

            status_list.append({
                "step_number": step_def["number"],
                "step_name": step_def["name"],
                "label": step_def["label"],
                "status": "approved" if approved else "in_progress",
                "has_approved": approved is not None,
                "version_count": len(versions) if versions else 0,
                "step_id": step.id,
            })

        return status_list

    def get_next_step(self, episode_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the next step that needs to be executed.

        Returns:
            Step definition dict, or None if all steps are complete
        """
        statuses = self.get_episode_status(episode_id)

        for status in statuses:
            if not status["has_approved"]:
                step_def = STEP_DEFINITIONS[status["step_number"] - 1]
                return {
                    **step_def,
                    "step_id": status.get("step_id"),
                }

        return None  # All steps approved

    @staticmethod
    def get_step_definitions() -> List[Dict[str, Any]]:
        """Get all step definitions."""
        return STEP_DEFINITIONS.copy()

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    def _get_step_record(self, episode_id: int, step_number: int):
        """Get Step DB record for an episode and step number."""
        session = self.repository.get_session()
        try:
            from src.data.models import Step
            step = session.query(Step).filter(
                Step.episode_id == episode_id,
                Step.step_number == step_number,
            ).first()
            return step
        finally:
            session.close()

    def _check_previous_approved(self, episode_id: int, step_number: int):
        """
        Check that the previous step has an approved version.

        Returns:
            (True, None) if OK, or (False, error_message) if not
        """
        prev_step = self._get_step_record(episode_id, step_number - 1)
        if not prev_step:
            return False, f"Previous step {step_number - 1} not found"

        approved = self.repository.get_approved_step_version(prev_step.id)
        if not approved:
            prev_def = STEP_DEFINITIONS[step_number - 2]
            return (
                False,
                f"이전 단계 '{prev_def['label']}'가 아직 승인되지 않았습니다. "
                f"먼저 이전 단계를 완료하고 승인해주세요.",
            )

        return True, None

    def _get_previous_context(
        self, episode_id: int, step_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get the approved content from the previous step as context.

        Returns:
            Context dictionary, or None if step 1 or no previous content
        """
        if step_number <= 1:
            return None

        prev_step = self._get_step_record(episode_id, step_number - 1)
        if not prev_step:
            return None

        approved = self.repository.get_approved_step_version(prev_step.id)
        if not approved:
            return None

        # Try to parse content as JSON, fall back to plain text
        try:
            return json.loads(approved.content)
        except (json.JSONDecodeError, TypeError):
            prev_def = STEP_DEFINITIONS[step_number - 2]
            return {
                "step": prev_def["name"],
                "label": prev_def["label"],
                "content": approved.content,
            }
