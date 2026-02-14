"""Tests for agent implementations."""

from unittest.mock import patch

from vors_ting.agents.creator import CreatorAgent
from vors_ting.agents.curator import CuratorAgent
from vors_ting.agents.reviewer import ReviewerAgent


def test_creator_agent() -> None:
    """Test creator agent functionality."""
    agent = CreatorAgent(
        name="TestCreator",
        role="creator",
        model="gpt-4",
        provider="openai",
        temperature=0.2,
    )

    assert agent.name == "TestCreator"
    assert agent.role == "creator"

    # Mock the LLM call
    with patch.object(agent, "_call_llm", return_value="Generated content"):
        result = agent.generate("Test task")
        assert result == "Generated content"


def test_reviewer_agent() -> None:
    """Test reviewer agent functionality."""
    agent = ReviewerAgent(
        name="TestReviewer",
        role="reviewer",
        model="gpt-4",
        provider="openai",
        temperature=0.2,
    )

    assert agent.name == "TestReviewer"
    assert agent.role == "reviewer"

    # Mock the LLM call
    with patch.object(agent, "_call_llm", return_value="Review feedback"):
        result = agent.review("Test content")
        assert "feedback" in result


def test_curator_agent() -> None:
    """Test curator agent functionality."""
    agent = CuratorAgent(
        name="TestCurator",
        role="curator",
        model="gpt-4",
        provider="openai",
        temperature=0.2,
    )

    assert agent.name == "TestCurator"
    assert agent.role == "curator"

    # Test clustering (placeholder implementation)
    ideas = ["Idea 1", "Idea 2", "Idea 3"]
    clusters = agent.cluster_ideas(ideas)
    assert len(clusters) == 1
    assert clusters[0] == ideas


def test_agent_rejection() -> None:
    """Test agent rejection functionality."""
    agent = CreatorAgent(
        name="TestAgent", role="creator", model="gpt-4", provider="openai"
    )

    result = agent.reject("Insufficient information")
    assert result["status"] == "rejected"
    assert result["reason"] == "Insufficient information"
