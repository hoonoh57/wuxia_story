"""
Gemini API Client - Wrapper with key rotation and retry logic

Handles:
- Multiple API key rotation
- Request retry with exponential backoff
- Error handling and logging
- Token usage tracking
"""

import json
import logging
import time
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Gemini API with key rotation and retry logic"""

    def __init__(
        self,
        api_keys: List[str],
        model: str = "gemini-2.5-flash",
        max_tokens: int = 8000,
        temperature: float = 0.8,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """
        Initialize Gemini Client.

        Args:
            api_keys: List of Gemini API keys for rotation
            model: Model name
            max_tokens: Maximum output tokens
            temperature: Generation temperature
            max_retries: Maximum retry attempts per request
            retry_delay: Base delay between retries (seconds)
        """
        if not api_keys:
            raise ValueError("At least one API key is required")

        self.api_keys = api_keys
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Key rotation state
        self._current_key_index = 0
        self._key_error_counts: Dict[int, int] = {i: 0 for i in range(len(api_keys))}

        # Usage tracking
        self._total_requests = 0
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_errors = 0

        # Initialize client with first key
        self._client = None
        self._init_client()

        logger.info(
            f"GeminiClient initialized: model={model}, "
            f"keys={len(api_keys)}, max_tokens={max_tokens}"
        )

    def _init_client(self):
        """Initialize or reinitialize the Gemini client with current key."""
        try:
            from google import genai

            self._client = genai.Client(
                api_key=self.api_keys[self._current_key_index]
            )
            logger.debug(f"Client initialized with key index {self._current_key_index}")
        except ImportError:
            logger.error(
                "google-genai package not installed. "
                "Run: pip install google-genai"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise

    def _rotate_key(self):
        """Rotate to next available API key."""
        if len(self.api_keys) <= 1:
            logger.warning("Only one API key available, cannot rotate")
            return False

        old_index = self._current_key_index
        self._current_key_index = (self._current_key_index + 1) % len(self.api_keys)
        self._init_client()
        logger.info(f"API key rotated: {old_index} → {self._current_key_index}")
        return True

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini API with retry and key rotation.

        Args:
            prompt: User prompt text
            system_prompt: Optional system instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens

        Returns:
            Dict with keys: text, input_tokens, output_tokens, model, success
        """
        from google.genai import types

        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        # Build generation config
        gen_config = types.GenerateContentConfig(
            temperature=temp,
            max_output_tokens=tokens,
        )

        # Add system instruction if provided
        if system_prompt:
            gen_config.system_instruction = system_prompt

        last_error = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(
                    f"Generating content (attempt {attempt + 1}/{self.max_retries}, "
                    f"key={self._current_key_index})"
                )

                response = self._client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=gen_config,
                )

                # Extract response
                text = response.text or ""

                # Track usage
                self._total_requests += 1
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0) or 0
                self._total_input_tokens += input_tokens
                self._total_output_tokens += output_tokens

                logger.info(
                    f"Generation successful: "
                    f"{input_tokens} in / {output_tokens} out tokens"
                )

                return {
                    "text": text,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "model": self.model,
                    "success": True,
                }

            except Exception as e:
                last_error = e
                self._total_errors += 1
                self._key_error_counts[self._current_key_index] += 1

                error_str = str(e).lower()
                logger.warning(f"Generation error (attempt {attempt + 1}): {e}")

                # Rotate key on quota/auth errors
                if "quota" in error_str or "429" in error_str or "403" in error_str:
                    if self._rotate_key():
                        continue

                # Exponential backoff for other errors
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay}s...")
                    time.sleep(delay)

        # All retries exhausted
        logger.error(f"All {self.max_retries} attempts failed. Last error: {last_error}")
        return {
            "text": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "model": self.model,
            "success": False,
            "error": str(last_error),
        }

    def generate_with_context(
        self,
        prompt: str,
        context: Dict[str, Any],
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate content with additional context injected into the prompt.

        Args:
            prompt: User prompt text
            context: Context dictionary to inject (previous step output, etc.)
            system_prompt: Optional system instruction

        Returns:
            Generation result dict
        """
        # Build context string
        context_str = json.dumps(context, ensure_ascii=False, indent=2)

        full_prompt = (
            f"=== CONTEXT (Previous Step Output) ===\n"
            f"{context_str}\n\n"
            f"=== CURRENT TASK ===\n"
            f"{prompt}"
        )

        return self.generate(full_prompt, system_prompt=system_prompt)

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self._total_requests,
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "total_errors": self._total_errors,
            "current_key_index": self._current_key_index,
            "key_error_counts": dict(self._key_error_counts),
        }

    def is_available(self) -> bool:
        """Check if client is properly initialized and ready."""
        return self._client is not None and len(self.api_keys) > 0
