"""
Dispatcher - Dual-mode dispatcher managing A/B/C workflow modes

Modes:
- A (HUMAN_RELAY): Human writes content via Claude/manual, pastes into system
- B (AUTO): Gemini generates content automatically, auto-saves as draft
- C (MIXED): Gemini generates draft, human reviews/edits, then approves

The dispatcher connects: UI → Agent → GeminiClient → Repository
"""

import logging
from enum import Enum
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class DispatchMode(Enum):
    """Dispatch mode enumeration"""
    HUMAN_RELAY = "A"
    AUTO = "B"
    MIXED = "C"


class DispatchResult:
    """Result object returned by dispatcher"""

    def __init__(
        self,
        success: bool,
        content: str = "",
        mode: str = "",
        needs_review: bool = False,
        version_id: Optional[int] = None,
        ai_response: Optional[Dict] = None,
        error: str = "",
    ):
        self.success = success
        self.content = content
        self.mode = mode
        self.needs_review = needs_review
        self.version_id = version_id
        self.ai_response = ai_response
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content": self.content,
            "mode": self.mode,
            "needs_review": self.needs_review,
            "version_id": self.version_id,
            "error": self.error,
        }


class Dispatcher:
    """Manages dual-mode dispatch for step execution"""

    def __init__(self, gemini_client, skill_loader, repository):
        """
        Initialize Dispatcher.

        Args:
            gemini_client: GeminiClient instance (can be None for mode A)
            skill_loader: SkillLoader instance
            repository: Repository instance for DB operations
        """
        self.gemini_client = gemini_client
        self.skill_loader = skill_loader
        self.repository = repository
        self.mode = DispatchMode.MIXED  # Default mode
        logger.info(f"Dispatcher initialized with mode: {self.mode.value}")

    def set_mode(self, mode: str):
        """Set execution mode (A, B, or C)."""
        self.mode = DispatchMode(mode)
        logger.info(f"Dispatcher mode changed to: {self.mode.value} ({self.mode.name})")

    def get_mode(self) -> str:
        """Get current mode as string."""
        return self.mode.value

    # ─────────────────────────────────────────────
    # Main dispatch method
    # ─────────────────────────────────────────────

    def execute_step(
        self,
        step_id: int,
        step_name: str,
        user_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        mode_override: Optional[str] = None,
    ) -> DispatchResult:
        """
        Execute a pipeline step based on current mode.

        Args:
            step_id: Database Step ID
            step_name: Step name (e.g., 'material_selection')
            user_prompt: The user's prompt or instruction for this step
            context: Previous step's approved output (auto-injected)
            mode_override: Override the dispatcher's default mode for this call

        Returns:
            DispatchResult with content and status
        """
        active_mode = DispatchMode(mode_override) if mode_override else self.mode
        logger.info(f"Executing step '{step_name}' (id={step_id}) in mode {active_mode.value}")

        if active_mode == DispatchMode.HUMAN_RELAY:
            return self._human_relay(step_id, user_prompt)
        elif active_mode == DispatchMode.AUTO:
            return self._auto_generate(step_id, step_name, user_prompt, context)
        else:
            return self._mixed_generate(step_id, step_name, user_prompt, context)

    # ─────────────────────────────────────────────
    # Mode A: Human Relay
    # ─────────────────────────────────────────────

    def _human_relay(
        self, step_id: int, user_content: str
    ) -> DispatchResult:
        """
        Mode A: Human provides content directly.
        Content is saved as a draft version for review.
        """
        if not user_content.strip():
            return DispatchResult(
                success=False,
                mode="A",
                error="No content provided. Please enter your content.",
            )

        # Save as draft
        version = self.repository.create_step_version(
            step_id=step_id,
            content=user_content,
            ai_generated=False,
            created_by="human_relay",
        )

        logger.info(f"Mode A: Human content saved as version {version.id}")

        return DispatchResult(
            success=True,
            content=user_content,
            mode="A",
            needs_review=False,
            version_id=version.id,
        )

    # ─────────────────────────────────────────────
    # Mode B: Fully Automated
    # ─────────────────────────────────────────────

    def _auto_generate(
        self,
        step_id: int,
        step_name: str,
        user_prompt: str,
        context: Optional[Dict[str, Any]],
    ) -> DispatchResult:
        """
        Mode B: Gemini generates content automatically.
        Result is saved as AI-generated draft.
        """
        if not self.gemini_client or not self.gemini_client.is_available():
            return DispatchResult(
                success=False,
                mode="B",
                error="Gemini client not available. Check API keys.",
            )

        # Build system prompt from skill files
        system_prompt = self.skill_loader.build_step_prompt(step_name)

        # Call Gemini
        if context:
            response = self.gemini_client.generate_with_context(
                prompt=user_prompt,
                context=context,
                system_prompt=system_prompt,
            )
        else:
            response = self.gemini_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
            )

        if not response["success"]:
            return DispatchResult(
                success=False,
                mode="B",
                error=response.get("error", "Gemini generation failed"),
                ai_response=response,
            )

        generated_text = response["text"]

        # Save as AI-generated draft
        version = self.repository.create_step_version(
            step_id=step_id,
            content=generated_text,
            ai_generated=True,
            created_by="gemini_auto",
        )

        logger.info(
            f"Mode B: Auto-generated and saved as version {version.id} "
            f"({response['input_tokens']}+{response['output_tokens']} tokens)"
        )

        return DispatchResult(
            success=True,
            content=generated_text,
            mode="B",
            needs_review=False,
            version_id=version.id,
            ai_response=response,
        )

    # ─────────────────────────────────────────────
    # Mode C: Mixed (AI draft → Human review)
    # ─────────────────────────────────────────────

    def _mixed_generate(
        self,
        step_id: int,
        step_name: str,
        user_prompt: str,
        context: Optional[Dict[str, Any]],
    ) -> DispatchResult:
        """
        Mode C: Gemini generates draft, marked for human review.
        Same as auto but flags needs_review=True.
        """
        if not self.gemini_client or not self.gemini_client.is_available():
            return DispatchResult(
                success=False,
                mode="C",
                error="Gemini client not available. Check API keys.",
            )

        # Build system prompt from skill files
        system_prompt = self.skill_loader.build_step_prompt(step_name)

        # Call Gemini
        if context:
            response = self.gemini_client.generate_with_context(
                prompt=user_prompt,
                context=context,
                system_prompt=system_prompt,
            )
        else:
            response = self.gemini_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
            )

        if not response["success"]:
            return DispatchResult(
                success=False,
                mode="C",
                error=response.get("error", "Gemini generation failed"),
                ai_response=response,
            )

        generated_text = response["text"]

        # Save as AI-generated draft (awaiting human review)
        version = self.repository.create_step_version(
            step_id=step_id,
            content=generated_text,
            ai_generated=True,
            created_by="gemini_assisted",
        )

        logger.info(
            f"Mode C: Draft generated, awaiting human review. "
            f"Version {version.id} "
            f"({response['input_tokens']}+{response['output_tokens']} tokens)"
        )

        return DispatchResult(
            success=True,
            content=generated_text,
            mode="C",
            needs_review=True,
            version_id=version.id,
            ai_response=response,
        )

    # ─────────────────────────────────────────────
    # Human edit & approval
    # ─────────────────────────────────────────────

    def save_human_edit(self, step_id: int, content: str) -> DispatchResult:
        """
        Save a human edit as a new draft version.

        Args:
            step_id: Step ID
            content: Edited content

        Returns:
            DispatchResult
        """
        version = self.repository.create_step_version(
            step_id=step_id,
            content=content,
            ai_generated=False,
            created_by="human_edit",
        )

        logger.info(f"Human edit saved as version {version.id}")

        return DispatchResult(
            success=True,
            content=content,
            mode=self.mode.value,
            needs_review=False,
            version_id=version.id,
        )

    def approve_version(self, version_id: int) -> DispatchResult:
        """
        Approve a step version, making it the official output.

        Args:
            version_id: StepVersion ID to approve

        Returns:
            DispatchResult
        """
        self.repository.approve_step_version(version_id)
        logger.info(f"Version {version_id} approved")

        return DispatchResult(
            success=True,
            mode=self.mode.value,
            version_id=version_id,
        )
