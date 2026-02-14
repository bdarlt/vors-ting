"""Base agent class for Vörs ting."""

from abc import ABC, abstractmethod
from typing import Any

from litellm import completion


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(  # noqa: PLR0913 - agent config requires these args
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

    def _call_llm(self, prompt: str, **kwargs: Any) -> str:
        """Call the LLM with the given prompt."""
        messages = [{"role": "system", "content": self.system_prompt}]
        if prompt:
            messages.append({"role": "user", "content": prompt})

        response = completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            **kwargs,
        )

        return response.choices[0].message.content

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
