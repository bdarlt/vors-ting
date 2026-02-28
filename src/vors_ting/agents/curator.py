"""Curator agent implementation."""

from typing import Any, override

from .base import BaseAgent


class CuratorAgent(BaseAgent):
    """Agent that curates and organizes content."""

    def _build_clustering_prompt(self, items: list[str]) -> str:
        """Build the clustering prompt (exposed for logging)."""
        prompt = "Organize the following items into coherent clusters:\n\n"
        for i, item in enumerate(items):
            prompt += f"Item {i + 1}:\n{item}\n\n"
        prompt += "Provide clusters with names and item assignments:"
        return prompt

    @override
    def generate(
        self, task: str, context: dict[str, Any] | None = None
    ) -> str:
        """Generate content (curators can generate if needed)."""
        prompt = f"Task: {task}"
        if context:
            prompt += f"\n\nContext: {context}"
        prompt += "\n\nPlease generate content:"

        return self._call_llm(prompt)

    @override
    def review(
        self, content: str, rubric: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Review content."""
        prompt = f"Review the following content:\n\n{content}"
        if rubric:
            prompt += f"\n\nEvaluation rubric: {rubric}"
        prompt += "\n\nProvide feedback:"

        response = self._call_llm(prompt)
        return {"feedback": response, "scores": {}}

    @override
    def refine(self, original: str, feedback: dict[str, Any]) -> str:
        """Refine content based on feedback."""
        prompt = f"Original content:\n\n{original}"
        prompt += f"\n\nFeedback received:\n\n{feedback}"
        prompt += "\n\nPlease refine the content based on this feedback:"

        return self._call_llm(prompt)

    def cluster(self, items: list[str]) -> dict[str, Any]:
        """Cluster items into groups."""
        prompt = self._build_clustering_prompt(items)
        response = self._call_llm(prompt)
        return {"clusters": response}
