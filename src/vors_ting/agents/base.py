"""Base agent class for Vörs ting."""

import random
import time
from abc import ABC, abstractmethod
from typing import Any

from litellm import completion
from litellm.exceptions import RateLimitError


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    # Retry configuration
    MAX_RETRIES: int = 5
    BASE_DELAY: float = 1.0
    MAX_DELAY: float = 60.0
    EXPONENTIAL_BASE: float = 2.0

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        role: str,
        model: str,
        provider: str,
        temperature: float = 0.2,
        system_prompt: str | None = None,
    ) -> None:
        """Initialize the agent."""
        self.name = name
        self.role = role
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.system_prompt = system_prompt or self._get_default_system_prompt()

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt based on agent role."""
        prompts = {
            "creator": (
                "You are a creative expert. Generate high-quality content "
                "based on the task."
            ),
            "reviewer": (
                "You are a critical reviewer. Evaluate content objectively "
                "and provide constructive feedback."
            ),
            "curator": (
                "You are a curator. Organize and synthesize diverse ideas "
                "into coherent clusters."
            ),
        }
        return prompts.get(self.role, "You are a helpful assistant.")

    def _get_retry_after(self, exception: RateLimitError) -> float | None:
        """Extract retry-after duration from rate limit error.

        Checks for retry-after in the exception response headers.
        Returns seconds to wait, or None if not found.
        """
        # Try to get headers from the exception
        headers = getattr(exception, "headers", None)
        if not headers:
            return None

        # Check for retry-after header (seconds or HTTP date)
        retry_after = headers.get("retry-after") or headers.get("Retry-After")
        if retry_after:
            try:
                # retry-after is usually in seconds
                return float(retry_after)
            except ValueError:
                # Could be an HTTP date string, skip for now
                pass

        # Check for x-ratelimit-reset (timestamp)
        reset_ts = headers.get("x-ratelimit-reset") or headers.get("X-RateLimit-Reset")
        if reset_ts:
            try:
                reset_time = float(reset_ts)
                # If it's a Unix timestamp
                min_unix_ts = 1_000_000_000  # Year 2001
                if reset_time > min_unix_ts:
                    wait_time = reset_time - time.time()
                    return max(0, wait_time)
                # If it's seconds from now
                return float(reset_ts)
            except ValueError:
                pass

        return None

    def _call_llm(self, prompt: str, **kwargs: Any) -> str:
        """Call the LLM with the given prompt, with retry logic for rate limits."""
        messages = [{"role": "system", "content": self.system_prompt}]
        if prompt:
            messages.append({"role": "user", "content": prompt})

        # Use provider/model format if provider specified, else model only
        model_str = f"{self.provider}/{self.model}" if self.provider else self.model

        last_exception: Exception | None = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = completion(
                    model=model_str,
                    messages=messages,
                    temperature=self.temperature,
                    **kwargs,
                )
                return response.choices[0].message.content

            except RateLimitError as e:
                last_exception = e

                # Check if we should retry
                if attempt >= self.MAX_RETRIES - 1:
                    break

                # Try to get retry-after from headers
                retry_after = self._get_retry_after(e)

                if retry_after is not None:
                    # Use provider's suggested wait time
                    delay = min(retry_after, self.MAX_DELAY)
                else:
                    # Exponential backoff with jitter
                    delay = min(
                        self.BASE_DELAY * (self.EXPONENTIAL_BASE**attempt),
                        self.MAX_DELAY,
                    )
                    # Add jitter (0-20% random)
                    delay *= 1 + random.uniform(0, 0.2)  # noqa: S311

                attempt_str = f"{attempt + 1}/{self.MAX_RETRIES}"
                print(  # noqa: T201
                    f"Rate limited ({self.name}). "
                    f"Retrying in {delay:.1f}s... (attempt {attempt_str})"
                )
                time.sleep(delay)

            except Exception:
                # Non-rate-limit errors, raise immediately
                raise

        # All retries exhausted
        raise last_exception or RuntimeError("Max retries exceeded")

    @abstractmethod
    def generate(self, task: str, context: dict[str, Any] | None = None) -> str:
        """Generate content based on the task."""

    @abstractmethod
    def review(
        self, content: str, rubric: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Review content and provide feedback."""

    @abstractmethod
    def refine(self, original: str, feedback: dict[str, Any]) -> str:
        """Refine content based on feedback."""

    def reject(self, reason: str) -> dict[str, Any]:
        """Reject the task with a reason."""
        return {"status": "rejected", "reason": reason}
