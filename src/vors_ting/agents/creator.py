"""Creator agent implementation."""

from typing import Any

from .base import BaseAgent


class CreatorAgent(BaseAgent):
    """Agent that generates content."""

    def generate(self, task: str, context: dict[str, Any] | None = None) -> str:
        """Generate content based on the task."""
        prompt = f"Task: {task}"
        if context:
            prompt += f"\n\nContext: {context}"
        prompt += "\n\nPlease generate high-quality content:"

        return self._call_llm(prompt)

    def review(
        self, content: str, rubric: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Review content as a creator (peer review)."""
        prompt = f"Review the following content:\n\n{content}"
        if rubric:
            prompt += f"\n\nEvaluation rubric: {rubric}"
        prompt += "\n\nProvide constructive feedback and scores:"

        response = self._call_llm(prompt)
        # Parse response into structured feedback
        return {"feedback": response, "scores": {}}

    def refine(self, original: str, feedback: dict[str, Any]) -> str:
        """Refine content based on feedback."""
        prompt = f"Original content:\n\n{original}"
        prompt += f"\n\nFeedback received:\n\n{feedback}"
        prompt += "\n\nPlease refine the content based on this feedback:"

        return self._call_llm(prompt)
