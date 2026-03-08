"""Base agent class for Vörs ting."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic_ai import Agent

T = TypeVar("T")


class BaseAgent(ABC):
    """Abstract base class for all agents."""

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
        self.name: str = name
        self.role: str = role
        self.model: str = model
        self.provider: str = provider
        self.temperature: float = temperature
        self.system_prompt: str = (
            system_prompt or self._get_default_system_prompt()
        )
        self._agent: Agent = self._create_agent()

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

    def _create_agent(self) -> Agent:
        """Create a Pydantic AI Agent instance."""
        model_str = f"{self.provider}:{self.model}" if self.provider else self.model
        return Agent(
            model=model_str, system_prompt=self.system_prompt, retries=3
        )

    async def _call_llm(
        self, prompt: str, output_type: type[T] | None = None
    ) -> str | T:
        """Call the LLM with the given prompt using Pydantic AI."""
        result = await self._agent.run(prompt, output_type=output_type)
        return result.output

    @abstractmethod
    async def generate(
        self, task: str, context: dict[str, Any] | None = None
    ) -> str:
        """Generate content based on the task."""

    @abstractmethod
    async def review(
        self, content: str, rubric: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Review content and provide feedback."""

    @abstractmethod
    async def refine(self, original: str, feedback: dict[str, Any]) -> str:
        """Refine content based on feedback."""

    def reject(self, reason: str) -> dict[str, Any]:
        """Reject the task with a reason."""
        return {"status": "rejected", "reason": reason}
