"""Tests for the orchestrator."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from vors_ting.core.config import AgentConfig, Config
from vors_ting.orchestration.orchestrator import Orchestrator


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
    assert (output_dir / "artifact_0.txt").exists()

    # Check content
    with open(output_dir / "artifact_0.txt") as f:
        content = f.read()
        assert content == "Test content"
