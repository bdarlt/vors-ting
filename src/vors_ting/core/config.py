"""Configuration loading and validation for Vörs ting."""

import os
from pathlib import Path
from typing import Any, ClassVar

import yaml
from pydantic import BaseModel, Field, field_validator

# Load provider metadata at module level
# providers.yaml is at project root (one level above src/)
PROVIDERS_FILE = Path(__file__).parent.parent.parent.parent / "providers.yaml"
_PROVIDER_METADATA: dict[str, Any] | None = None


def get_provider_metadata() -> dict[str, Any]:
    """Load provider metadata from providers.yaml."""
    global _PROVIDER_METADATA  # noqa: PLW0603
    if _PROVIDER_METADATA is None:
        if PROVIDERS_FILE.exists():
            with PROVIDERS_FILE.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                _PROVIDER_METADATA = data.get("providers", {})
        else:
            _PROVIDER_METADATA = {}
    return _PROVIDER_METADATA


def validate_provider(provider: str, temperature: float) -> list[str]:
    """Validate provider and temperature against metadata.

    Returns a list of warning messages.
    """
    warnings = []
    metadata = get_provider_metadata()

    if not provider:
        # Using full model string format, skip provider-specific validation
        return warnings

    provider_key = provider.lower()

    if provider_key not in metadata:
        warnings.append(
            f"Unknown provider '{provider}'. Add to providers.yaml for validation."
        )
        return warnings

    provider_info = metadata[provider_key]

    # Check temperature range
    temp_range = provider_info.get("temperature", {})
    temp_min = temp_range.get("min", 0.0)
    temp_max = temp_range.get("max", 2.0)

    if temperature < temp_min or temperature > temp_max:
        warnings.append(
            f"Temperature {temperature} outside recommended range "
            f"[{temp_min}, {temp_max}] for {provider}"
        )

    # Check API key
    api_key_env = provider_info.get("api_key_env")
    if api_key_env and api_key_env not in os.environ:
        warnings.append(f"API key env var '{api_key_env}' not set for {provider}")

    return warnings


class AgentConfig(BaseModel):
    """Configuration for a single agent."""

    name: str
    role: str  # creator, reviewer, curator
    model: str
    provider: str | None = None
    temperature: float = 0.2
    system_prompt: str | None = None
    file: str | None = None  # External prompt file

    TEMP_MAX: ClassVar[float] = 5.0

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature is within reasonable bounds."""
        if v < 0 or v > cls.TEMP_MAX:
            msg = f"Temperature must be between 0 and {cls.TEMP_MAX}"
            raise ValueError(msg)
        return v

    def model_post_init(self, _context: Any, /) -> None:
        """Load system prompt from file if specified."""
        if self.file and not self.system_prompt:
            file_path = Path(self.file)
            if not file_path.is_absolute():
                # Resolve relative to CWD
                file_path = Path.cwd() / file_path

            if file_path.exists():
                self.system_prompt = file_path.read_text(encoding="utf-8")
            else:
                msg = f"Prompt file not found: {self.file}"
                raise ValueError(msg)


class RubricCriterion(BaseModel):
    """A single criterion in the evaluation rubric."""

    name: str
    weight: float
    guidelines: str


class RubricConfig(BaseModel):
    """Configuration for the evaluation rubric."""

    criteria: list[RubricCriterion]
    living: bool = False
    shadow_path: str | None = None


class ConvergenceConfig(BaseModel):
    """Configuration for convergence detection."""

    method: str = "consensus"  # consensus, similarity, hybrid
    similarity_threshold: float = 0.95
    max_rounds: int = 5
    triage: bool = True


class SafeguardsConfig(BaseModel):
    """Configuration for safeguards."""

    devil_advocate: dict[str, Any] = Field(default_factory=dict)
    rejection_option: bool = True
    shadow_rubric: dict[str, Any] = Field(default_factory=dict)


class MetricsConfig(BaseModel):
    """Configuration for metrics logging."""

    log_dir: str = "metrics/"
    regret_tracking: bool = True
    dissent_impact: bool = True
    escalation_usefulness: bool = True


class DivergenceConfig(BaseModel):
    """Configuration for divergence mode."""

    min_clusters: int = 3
    clustering_method: str = "embedding"
    curator_model: str = "gpt-4-turbo"
    human_sensemaker: bool = True


class Config(BaseModel):
    """Main configuration for Vörs ting."""

    task: str
    artifact_type: str
    agents: list[AgentConfig]
    rounds: int = 5
    mode: str = "converge"  # converge or diverge
    rubric: RubricConfig | None = None
    convergence: ConvergenceConfig = Field(default_factory=ConvergenceConfig)
    safeguards: SafeguardsConfig = Field(default_factory=SafeguardsConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    divergence: DivergenceConfig = Field(default_factory=DivergenceConfig)
    skill_prompts: dict[str, str] = Field(default_factory=dict)

    @field_validator("agents")
    @classmethod
    def validate_agents(cls, v: list[AgentConfig]) -> list[AgentConfig]:
        """Validate that at least one agent is configured."""
        if not v:
            error_msg = "At least one agent must be configured"
            raise ValueError(error_msg)
        return v

    @field_validator("rounds")
    @classmethod
    def validate_rounds(cls, v: int) -> int:
        """Validate that rounds is a positive integer."""
        if v <= 0:
            error_msg = "Rounds must be a positive integer"
            raise ValueError(error_msg)
        return v

    def validate_providers(self) -> list[str]:
        """Validate all agent providers and return warnings."""
        warnings: list[str] = []
        for agent in self.agents:
            agent_warnings = validate_provider(agent.provider or "", agent.temperature)
            warnings.extend(f"[{agent.name}] {w}" for w in agent_warnings)
        return warnings


def load_config(config_path: Path, verbose: bool = True) -> Config:
    """Load configuration from YAML file.

    Args:
        config_path: Path to YAML configuration file
        verbose: Whether to print validation warnings

    Returns:
        Config object

    """
    with config_path.open(encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    config = Config(**config_data)

    # Validate providers and show warnings
    if verbose:
        warnings = config.validate_providers()
        for warning in warnings:
            print(f"WARN: {warning}")  # noqa: T201
        if warnings:
            print()  # noqa: T201  # Extra newline after warnings

    return config
