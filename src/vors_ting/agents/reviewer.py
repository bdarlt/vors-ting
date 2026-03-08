"""Reviewer agent implementation."""

from typing import Any, cast, override

from vors_ting.agents.schemas import ReviewResult

from .base import BaseAgent


class ReviewerAgent(BaseAgent):
    """Agent that reviews content."""

    def _build_review_prompt(
        self, content: str, rubric: dict[str, Any] | None = None
    ) -> str:
        """Build the review prompt (exposed for logging)."""
        prompt = f"Review the following content:\n\n{content}"
        if rubric:
            prompt += f"\n\nEvaluation rubric: {rubric}"
        prompt += "\n\nProvide detailed feedback and scores for each criterion:"
        return prompt

    @override
    async def generate(
        self, task: str, context: dict[str, Any] | None = None
    ) -> str:
        """Generate content (reviewers can also generate if needed)."""
        prompt = f"Task: {task}"
        if context:
            prompt += f"\n\nContext: {context}"
        prompt += "\n\nPlease generate content:"

        return await self._call_llm(prompt)

    @override
    async def review(
        self, content: str, rubric: dict[str, Any] | None = None
    ) -> ReviewResult:
        """Review content and provide structured feedback."""
        prompt = self._build_review_prompt(content, rubric)
        result = await self._call_llm(prompt, output_type=ReviewResult)
        return cast("ReviewResult", result)

    @override
    async def refine(self, original: str, feedback: dict[str, Any]) -> str:
        """Refine content based on feedback."""
        prompt = f"Original content:\n\n{original}"
        prompt += f"\n\nFeedback received:\n\n{feedback}"
        prompt += "\n\nPlease refine the content based on this feedback:"

        return await self._call_llm(prompt)
