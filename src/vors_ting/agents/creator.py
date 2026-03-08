"""Creator agent implementation."""

from typing import Any, cast, override

from vors_ting.agents.base import BaseAgent
from vors_ting.agents.schemas import GenerationResult, ReviewResult


class CreatorAgent(BaseAgent):
    """Agent that generates content."""

    def _build_generation_prompt(
        self, task: str, context: dict[str, Any] | None = None
    ) -> str:
        """Build the generation prompt (exposed for logging)."""
        prompt = f"Task: {task}"
        if context:
            prompt += f"\n\nContext: {context}"
        prompt += "\n\nPlease generate high-quality content:"
        return prompt

    def _build_refinement_prompt(self, original: str, feedback: dict[str, Any]) -> str:
        """Build the refinement prompt (exposed for logging)."""
        prompt = f"Original content:\n\n{original}"
        prompt += f"\n\nFeedback received:\n\n{feedback}"
        prompt += "\n\nPlease refine the content based on this feedback:"
        return prompt

    @override
    async def generate(
        self, task: str, context: dict[str, Any] | None = None
    ) -> str:
        """Generate content based on the task."""
        prompt = self._build_generation_prompt(task, context)
        result = await self._call_llm(prompt, output_type=GenerationResult)
        typed_result = cast("GenerationResult", result)
        return typed_result.content

    @override
    async def review(
        self, content: str, rubric: dict[str, Any] | None = None
    ) -> ReviewResult:
        """Review content as a creator (peer review)."""
        prompt = f"Review the following content:\n\n{content}"
        if rubric:
            prompt += f"\n\nEvaluation rubric: {rubric}"
        prompt += "\n\nProvide constructive feedback and scores:"

        result = await self._call_llm(prompt, output_type=ReviewResult)
        return cast("ReviewResult", result)

    @override
    async def refine(self, original: str, feedback: dict[str, Any]) -> str:
        """Refine content based on feedback."""
        prompt = self._build_refinement_prompt(original, feedback)
        result = await self._call_llm(prompt, output_type=GenerationResult)
        typed_result = cast("GenerationResult", result)
        return typed_result.content
