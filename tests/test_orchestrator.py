"""Tests for the orchestrator."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vors_ting.core.config import AgentConfig, Config, MetricsConfig


# Import Orchestrator after patching
def get_orchestrator_class():
    """Get Orchestrator class with mocked dependencies."""
    from vors_ting.orchestration.orchestrator import Orchestrator

    return Orchestrator


def test_log_interaction(mock_sentence_transformers) -> None:  # noqa: ARG001
    """Test that _log_interaction captures prompt/response data."""
    orchestrator_class = get_orchestrator_class()
    config = Config(
        task="Test task",
        artifact_type="adr",
        agents=[
            AgentConfig(
                name="Creator1", role="creator", model="gpt-4", provider="openai"
            )
        ],
        rounds=1,
    )

    orchestrator = orchestrator_class(config)
    # Initialize round_history with a round entry
    orchestrator.round_history = [{"round": 0, "artifacts": []}]

    # Log an interaction
    orchestrator._log_interaction(
        round_num=0,
        agent_name="Creator1",
        agent_role="creator",
        prompt="Generate an ADR",
        response="The ADR content",
        metadata={"task": "Test task", "phase": "initial"},
    )

    # Verify interaction was logged
    assert "interactions" in orchestrator.round_history[-1]
    assert len(orchestrator.round_history[-1]["interactions"]) == 1

    interaction = orchestrator.round_history[-1]["interactions"][0]
    assert interaction["round"] == 0
    assert interaction["agent_name"] == "Creator1"
    assert interaction["agent_role"] == "creator"
    assert interaction["prompt"] == "Generate an ADR"
    assert interaction["response"] == "The ADR content"
    assert interaction["metadata"]["phase"] == "initial"
    assert "timestamp" in interaction


@pytest.mark.asyncio
async def test_auto_save(mock_sentence_transformers, tmp_path: Path) -> None:  # noqa: ARG001
    """Test that _auto_save creates logging output with interactions."""
    orchestrator_class = get_orchestrator_class()
    config = Config(
        task="Test task",
        artifact_type="adr",
        agents=[
            AgentConfig(
                name="Creator1", role="creator", model="gpt-4", provider="openai"
            )
        ],
        rounds=1,
        metrics=MetricsConfig(log_dir=str(tmp_path)),
    )

    orchestrator = orchestrator_class(config, quiet=True)
    orchestrator.current_round = 1
    orchestrator.round_history = [
        {
            "round": 0,
            "artifacts": ["Test artifact content"],
            "interactions": [
                {
                    "timestamp": "2024-01-01T00:00:00+00:00",
                    "round": 0,
                    "agent_name": "Creator1",
                    "agent_role": "creator",
                    "prompt": "Generate content",
                    "response": "Test artifact content",
                    "metadata": {"phase": "initial"},
                }
            ],
        }
    ]

    output_dir = await orchestrator._auto_save()

    # Check that all expected files were created
    assert (output_dir / "run_history.json").exists()
    assert (output_dir / "artifact_0.md").exists()
    assert (output_dir / "summary.txt").exists()

    # Check run_history.json contains full interaction data
    with (output_dir / "run_history.json").open() as f:
        run_history = json.load(f)

    assert run_history["config"]["task"] == "Test task"
    assert run_history["rounds_completed"] == 1
    assert len(run_history["round_history"]) == 1
    assert "interactions" in run_history["round_history"][0]
    assert len(run_history["round_history"][0]["interactions"]) == 1

    # Check artifact file
    with (output_dir / "artifact_0.md").open() as f:
        assert f.read() == "Test artifact content"

    # Check summary file
    with (output_dir / "summary.txt").open(encoding="utf-8") as f:
        summary = f.read()
        assert "Run Summary" in summary  # Check key phrase (unicode-safe)
        assert "Test task" in summary


def test_log_interaction_multiple_rounds(mock_sentence_transformers) -> None:  # noqa: ARG001
    """Test logging interactions across multiple rounds."""
    orchestrator_class = get_orchestrator_class()
    config = Config(
        task="Test task",
        artifact_type="adr",
        agents=[
            AgentConfig(
                name="Creator1", role="creator", model="gpt-4", provider="openai"
            ),
            AgentConfig(
                name="Reviewer1", role="reviewer", model="gpt-4", provider="openai"
            ),
        ],
        rounds=2,
    )

    orchestrator = orchestrator_class(config)

    # Simulate round 0
    orchestrator.round_history = [{"round": 0, "artifacts": ["Artifact 1"]}]
    orchestrator._log_interaction(
        round_num=0,
        agent_name="Creator1",
        agent_role="creator",
        prompt="Generate",
        response="Artifact 1",
        metadata={"phase": "initial"},
    )

    # Simulate round 1 with review
    orchestrator.round_history.append({"round": 1, "artifacts": ["Artifact 1 refined"]})
    orchestrator._log_interaction(
        round_num=1,
        agent_name="Reviewer1",
        agent_role="reviewer",
        prompt="Review",
        response='{"feedback": "Good"}',
        metadata={"phase": "review"},
    )
    orchestrator._log_interaction(
        round_num=1,
        agent_name="Creator1",
        agent_role="creator",
        prompt="Refine",
        response="Artifact 1 refined",
        metadata={"phase": "refinement"},
    )

    # Verify interactions are in correct rounds
    assert len(orchestrator.round_history[0]["interactions"]) == 1
    assert len(orchestrator.round_history[1]["interactions"]) == 2

    # Verify round 1 interactions
    interactions = orchestrator.round_history[1]["interactions"]
    assert interactions[0]["agent_role"] == "reviewer"
    assert interactions[1]["agent_role"] == "creator"


def test_orchestrator_initialization(mock_sentence_transformers) -> None:  # noqa: ARG001
    """Test orchestrator initialization."""
    orchestrator_class = get_orchestrator_class()
    config = Config(
        task="Test task",
        artifact_type="adr",
        agents=[
            AgentConfig(
                name="Creator1", role="creator", model="gpt-4", provider="openai"
            )
        ],
        rounds=3,
    )

    orchestrator = orchestrator_class(config)
    assert orchestrator.config == config
    assert len(orchestrator.agents) == 0
    assert orchestrator.current_round == 0


def test_agent_initialization(mock_sentence_transformers) -> None:  # noqa: ARG001
    """Test agent initialization."""
    orchestrator_class = get_orchestrator_class()
    config = Config(
        task="Test task",
        artifact_type="adr",
        agents=[
            AgentConfig(
                name="Creator1", role="creator", model="gpt-4", provider="openai"
            ),
            AgentConfig(
                name="Reviewer1", role="reviewer", model="gpt-4", provider="openai"
            ),
        ],
        rounds=3,
    )

    orchestrator = orchestrator_class(config)

    # Patch _create_agent on agent classes to avoid API key requirement
    with (
        patch(
            "vors_ting.orchestration.orchestrator.CreatorAgent._create_agent",
            return_value=None,
        ),
        patch(
            "vors_ting.orchestration.orchestrator.ReviewerAgent._create_agent",
            return_value=None,
        ),
    ):
        orchestrator.initialize_agents()

    assert len(orchestrator.agents) == 2
    assert orchestrator.agents[0].name == "Creator1"
    assert orchestrator.agents[1].name == "Reviewer1"


@pytest.mark.asyncio
async def test_converge_mode(mock_sentence_transformers) -> None:  # noqa: ARG001
    """Test converge mode execution."""
    orchestrator_class = get_orchestrator_class()
    # Setup mock agents with async methods
    mock_creator_instance = MagicMock()
    mock_creator_instance.role = "creator"
    mock_creator_instance.generate = AsyncMock(return_value="Initial content")
    mock_creator_instance.refine = AsyncMock(return_value="Refined content")

    mock_reviewer_instance = MagicMock()
    mock_reviewer_instance.role = "reviewer"
    mock_reviewer_instance.review = AsyncMock(return_value={"feedback": "Good job"})

    config = Config(
        task="Test task",
        artifact_type="adr",
        agents=[
            AgentConfig(
                name="Creator1", role="creator", model="gpt-4", provider="openai"
            ),
            AgentConfig(
                name="Reviewer1", role="reviewer", model="gpt-4", provider="openai"
            ),
        ],
        rounds=2,
    )

    orchestrator = orchestrator_class(config)

    with (
        patch(
            "vors_ting.orchestration.orchestrator.CreatorAgent",
            return_value=mock_creator_instance,
        ),
        patch(
            "vors_ting.orchestration.orchestrator.ReviewerAgent",
            return_value=mock_reviewer_instance,
        ),
        patch.object(
            orchestrator, "_check_convergence", side_effect=[False, True]
        ),
    ):
        result = await orchestrator.run()

    assert result["status"] == "converged"
    assert orchestrator.current_round == 2


def test_save_state(mock_sentence_transformers, tmp_path: Path) -> None:  # noqa: ARG001
    """Test saving orchestrator state."""
    orchestrator_class = get_orchestrator_class()
    config = Config(
        task="Test task",
        artifact_type="adr",
        agents=[
            AgentConfig(
                name="Creator1", role="creator", model="gpt-4", provider="openai"
            )
        ],
        rounds=1,
    )

    orchestrator = orchestrator_class(config)
    orchestrator.round_history = [{"round": 0, "artifacts": ["Test content"]}]

    output_dir = tmp_path / "output"
    orchestrator.save_state(output_dir)

    # Check that files were created
    assert (output_dir / "round_history.json").exists()
    # ADR artifact type uses .md extension
    assert (output_dir / "artifact_0.md").exists()

    # Check content
    with (output_dir / "artifact_0.md").open() as f:
        content = f.read()
        assert content == "Test content"
