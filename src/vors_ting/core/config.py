"""Configuration loading and validation for Vörs ting."""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, validator


class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    name: str
    role: str  # creator, reviewer, curator
    model: str
    provider: str
    temperature: float = 0.2
    system_prompt: Optional[str] = None


class RubricCriterion(BaseModel):
    """A single criterion in the evaluation rubric."""
    name: str
    weight: float
    guidelines: str


class RubricConfig(BaseModel):
    """Configuration for the evaluation rubric."""
    criteria: List[RubricCriterion]
    living: bool = False
    shadow_path: Optional[str] = None


class ConvergenceConfig(BaseModel):
    """Configuration for convergence detection."""
    method: str = "consensus"  # consensus, similarity, hybrid
    similarity_threshold: float = 0.95
    max_rounds: int = 5
    triage: bool = True


class SafeguardsConfig(BaseModel):
    """Configuration for safeguards."""
    devil_advocate: Dict[str, Any] = Field(default_factory=dict)
    rejection_option: bool = True
    shadow_rubric: Dict[str, Any] = Field(default_factory=dict)


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
    agents: List[AgentConfig]
    rounds: int = 5
    mode: str = "converge"  # converge or diverge
    rubric: Optional[RubricConfig] = None
    convergence: ConvergenceConfig = Field(default_factory=ConvergenceConfig)
    safeguards: SafeguardsConfig = Field(default_factory=SafeguardsConfig)
    metrics: MetricsConfig = Field(default_factory=MetricsConfig)
    divergence: DivergenceConfig = Field(default_factory=DivergenceConfig)
    skill_prompts: Dict[str, str] = Field(default_factory=dict)

    @validator("agents")
    def validate_agents(cls, v: List[AgentConfig]) -> List[AgentConfig]:
        """Validate that at least one agent is configured."""
        if not v:
            raise ValueError("At least one agent must be configured")
        return v

    @validator("rounds")
    def validate_rounds(cls, v: int) -> int:
        """Validate that rounds is a positive integer."""
        if v <= 0:
            raise ValueError("Rounds must be a positive integer")
        return v


def load_config(config_path: Path) -> Config:
    """Load configuration from YAML file."""
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)
    
    return Config(**config_data)
