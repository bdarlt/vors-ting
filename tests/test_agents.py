"""Tests for agent implementations."""

from unittest.mock import patch

import pytest
from pydantic_ai import Agent
from pydantic_ai.models.test import TestModel

from vors_ting.agents.creator import CreatorAgent
from vors_ting.agents.curator import CuratorAgent
from vors_ting.agents.reviewer import ReviewerAgent
from vors_ting.agents.schemas import GenerationResult, ReviewResult


@pytest.mark.asyncio
async def test_creator_agent() -> None:
    """Test creator agent functionality."""
    # Patch _create_agent to avoid API key requirement during init
    with patch.object(CreatorAgent, "_create_agent", return_value=None):
        agent = CreatorAgent(
            name="TestCreator",
            role="creator",
            model="gpt-4",
            provider="openai",
            temperature=0.2,
        )

    assert agent.name == "TestCreator"
    assert agent.role == "creator"

    # Create test model with custom output args for structured output
    test_model = TestModel(
        custom_output_args=GenerationResult(
            content="Generated content", confidence=8, citations=[]
        ).model_dump()
    )
    agent._agent = Agent(test_model, system_prompt=agent.system_prompt)

    result = await agent.generate("Test task")
    assert result == "Generated content"


@pytest.mark.asyncio
async def test_reviewer_agent() -> None:
    """Test reviewer agent functionality."""
    # Patch _create_agent to avoid API key requirement during init
    with patch.object(ReviewerAgent, "_create_agent", return_value=None):
        agent = ReviewerAgent(
            name="TestReviewer",
            role="reviewer",
            model="gpt-4",
            provider="openai",
            temperature=0.2,
        )

    assert agent.name == "TestReviewer"
    assert agent.role == "reviewer"

    # Create test model with custom output args for structured output
    test_model = TestModel(
        custom_output_args=ReviewResult(
            feedback="Review feedback",
            clarity_score=7,
            completeness_score=8,
            security_concerns=[],
        ).model_dump()
    )
    agent._agent = Agent(test_model, system_prompt=agent.system_prompt)

    result = await agent.review("Test content")
    assert isinstance(result, ReviewResult)
    assert result.feedback == "Review feedback"
    assert result.clarity_score == 7


@pytest.mark.asyncio
async def test_curator_agent() -> None:
    """Test curator agent functionality."""
    # Patch _create_agent to avoid API key requirement during init
    with patch.object(CuratorAgent, "_create_agent", return_value=None):
        agent = CuratorAgent(
            name="TestCurator",
            role="curator",
            model="gpt-4",
            provider="openai",
            temperature=0.2,
        )

    assert agent.name == "TestCurator"
    assert agent.role == "curator"

    # Create test model with custom output text for string output
    test_model = TestModel(custom_output_text="Cluster 1: Idea 1, Idea 2")
    agent._agent = Agent(test_model, system_prompt=agent.system_prompt)

    ideas = ["Idea 1", "Idea 2", "Idea 3"]
    result = await agent.cluster(ideas)
    assert "clusters" in result


def test_agent_rejection() -> None:
    """Test agent rejection functionality."""
    # Patch _create_agent to avoid API key requirement during init
    with patch.object(CreatorAgent, "_create_agent", return_value=None):
        agent = CreatorAgent(
            name="TestAgent", role="creator", model="gpt-4", provider="openai"
        )

    result = agent.reject("Insufficient information")
    assert result["status"] == "rejected"
    assert result["reason"] == "Insufficient information"
