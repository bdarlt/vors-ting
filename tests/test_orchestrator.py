"""Tests for the orchestrator."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from vors_ting.core.config import AgentConfig, Config, MetricsConfig
from vors_ting.orchestration.orchestrator import Orchestrator


def test_log_interaction() -> None:
    """Test that _log_interaction captures prompt/response data."""
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

    orchestrator = Orchestrator(config)
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


def test_auto_save(tmp_path: Path) -> None:
    """Test that _auto_save creates logging output with interactions."""
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

    orchestrator = Orchestrator(config, quiet=True)
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

    output_dir = orchestrator._auto_save()

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


def test_log_interaction_multiple_rounds() -> None:
    """Test logging interactions across multiple rounds."""
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

    orchestrator = Orchestrator(config)

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


def test_orchestrator_initialization() -> None:
    """Test orchestrator initialization."""
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

    orchestrator = Orchestrator(config)
    assert orchestrator.config == config
    assert len(orchestrator.agents) == 0
    assert orchestrator.current_round == 0


def test_agent_initialization() -> None:
    """Test agent initialization."""
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

    orchestrator = Orchestrator(config)
    orchestrator.initialize_agents()

    assert len(orchestrator.agents) == 2
    assert orchestrator.agents[0].name == "Creator1"
    assert orchestrator.agents[1].name == "Reviewer1"


@patch("vors_ting.orchestration.orchestrator.CreatorAgent")
@patch("vors_ting.orchestration.orchestrator.ReviewerAgent")
def test_converge_mode(mock_reviewer, mock_creator) -> None:
    """Test converge mode execution."""
    # Setup mock agents
    mock_creator_instance = MagicMock()
    mock_creator_instance.role = "creator"
    mock_creator_instance.generate.return_value = "Initial content"
    mock_creator_instance.refine.return_value = "Refined content"
    mock_creator.return_value = mock_creator_instance

    mock_reviewer_instance = MagicMock()
    mock_reviewer_instance.role = "reviewer"
    mock_reviewer_instance.review.return_value = {"feedback": "Good job"}
    mock_reviewer.return_value = mock_reviewer_instance

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

    orchestrator = Orchestrator(config)

    # Mock convergence check to return True on second round
    with patch.object(orchestrator, "_check_convergence", side_effect=[False, True]):
        result = orchestrator.run()

    assert result["status"] == "converged"
    assert orchestrator.current_round == 2


def test_save_state(tmp_path: Path) -> None:
    """Test saving orchestrator state."""
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

    orchestrator = Orchestrator(config)
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
