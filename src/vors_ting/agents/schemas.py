"""Structured output schemas for agents using Pydantic."""

from pydantic import BaseModel, Field


class ReviewResult(BaseModel):
    """Structured output from reviewer agents."""

    feedback: str = Field(description="Detailed constructive feedback")
    clarity_score: int = Field(
        ge=1, le=10, description="Clarity rating from 1 to 10"
    )
    completeness_score: int = Field(
        ge=1, le=10, description="Completeness rating from 1 to 10"
    )
    security_concerns: list[str] = Field(
        default_factory=list, description="List of security concerns"
    )

    @property
    def overall_score(self) -> float:
        """Calculate overall score as average of clarity and completeness."""
        return (self.clarity_score + self.completeness_score) / 2


class GenerationResult(BaseModel):
    """Structured output from creator agents."""

    content: str = Field(description="Generated content")
    confidence: int = Field(
        ge=1, le=10, description="Confidence rating from 1 to 10"
    )
    citations: list[str] = Field(
        default_factory=list, description="List of citations"
    )
