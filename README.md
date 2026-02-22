# Vörs ting

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

<!-- CI/CD Badges -->
[![CI Status](https://github.com/bdarlt/vors-ting/actions/workflows/ci.yml/badge.svg)](https://github.com/bdarlt/vors-ting/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badges/v2.json)](https://github.com/astral-sh/ruff)
[![Pyright](https://img.shields.io/badge/type--checked-pyright-blue)](https://github.com/microsoft/pyright)
[![pytest](https://img.shields.io/badge/tested_with-pytest-blue)](https://docs.pytest.org/)
[![Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://www.mkdocs.org/)

Vörs ting is a multi‑agent workflow tool for iterative feedback loops that drive
convergent (and optionally divergent) refinement of work products. Inspired by
the Norse goddess **Vör**, from whom nothing can be hidden, and the ancient
***ting*** assembly, it orchestrates AI agents to critique, debate, and improve
artifacts until wisdom is reached.

## Table of Contents

- [Vörs ting](#vörs-ting)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Quick Start](#quick-start)
    - [Command Reference](#command-reference)
    - [Agent Patterns](#agent-patterns)
  - [Configuration](#configuration)
  - [Contributing](#contributing)
  - [License](#license)
  - [Roadmap](#roadmap)
  - [FAQ](#faq)
  - [Contact](#contact)

## Description

Vörs ting is a Python-based scaffolding that automates structured, multi-agent feedback loops. It helps you create higher-quality outputs—like ADRs, unit tests, or process docs—by systematically exposing work to adversarial and collaborative critique, iterating until a convergence of wisdom is achieved.

## Installation

**Prerequisites:** Python 3.13+ and [uv](https://docs.astral.sh/uv/).

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/bdarlt/vors-ting.git
    cd vors-ting
    ```

2.  **Install the package:**
    ```bash
    uv sync
    ```

3.  **Set up API keys:**
    Vörs ting uses LiteLLM to connect to LLM providers. Set your API keys as environment variables:
    ```bash
    export ANTHROPIC_API_KEY="your-key-here"
    export OPENAI_API_KEY="your-key-here"
    export GOOGLE_API_KEY="your-key-here"
    export MOONSHOT_API_KEY="your-key-here"
    export DEEPSEEK_API_KEY="your-key-here"
    export MISTRAL_API_KEY="your-key-here"
    ```

## Usage

Vörs ting runs via CLI with a YAML configuration file.

### Quick Start

1.  **Create a config file** (`my_review.yaml`):
    ```yaml
    task: "Write an ADR for migrating from REST to GraphQL"
    artifact_type: "adr"
    agents:
      - name: "Creator"
        role: "creator"
        model: "kimi-k2.5"
        provider: "moonshot"
      - name: "Skeptic"
        role: "reviewer"
        model: "gemini-1.5-pro"
        provider: "google"
    rounds: 5
    mode: "converge"
    ```

2.  **Run it:**
    ```bash
    uv run vors run my_review.yaml
    ```

3.  **View output:**
    Results are saved to `output/` by default (or specify with `--output dir/`).

### Command Reference

```bash
# Basic run (verbose output shows LLM calls, feedback, previews)
uv run vors run config.yaml

# Quiet mode (suppress verbose output)
uv run vors run config.yaml --quiet
# or
uv run vors run config.yaml -q

# Specify output directory
uv run vors run config.yaml --output ./results

# Run example configs
uv run vors run examples/simple_config.yaml
uv run vors run examples/polyadic_config.yaml

# Using main.py entry point
uv run python main.py run config.yaml
```

### Agent Patterns

**Dyadic (Creator + Reviewer):** One creator writes, one reviewer critiques (default).

**Polyadic (Multiple Creators):** Multiple creators write independently, then review each other's work. Define multiple agents with `role: creator`.

## Configuration

See `examples/` for complete config files. Key options:

```yaml
task: "What you want the agents to create"
artifact_type: "adr"  # adr | test | doc | cursor-rules | meeting | generic

agents:
  - name: "Creator1"
    role: "creator"      # creator | reviewer | curator
    model: "claude-3-opus-20240229"
    provider: "anthropic"  # LiteLLM provider (optional)
    temperature: 0.7
    file: "prompts/custom.md"  # External system prompt (optional)
  - name: "Skeptic"
    role: "reviewer"
    model: "gemini-1.5-pro"
    provider: "google"

rounds: 5              # Maximum iterations
mode: "converge"       # converge | diverge

convergence:
  similarity_threshold: 0.95  # Stop early if artifacts are similar enough

rubric:                # Optional evaluation criteria
  criteria:
    - name: "Accuracy"
      weight: 0.4
      guidelines: "Check facts against known sources"
```

### Model Format

LiteLLM uses `provider/model-name` format. You can specify this two ways:

```yaml
# Option 1: Separate provider and model (recommended)
provider: "mistral"
model: "devstral-latest"
# Results in: mistral/devstral-latest

# Option 2: Full model string, no provider
provider: null
model: "openai/gpt-4"
# Results in: openai/gpt-4
```

For full configuration reference, see [Configuration Guide](docs/configuration.md).

## Contributing

We warmly welcome contributions! Whether it's reporting a bug, discussing a new feature, or submitting a pull request, please follow our guidelines.

Please see our [Contributing Guide](CONTRIBUTING.md) for more details on how to get involved. All contributors are expected to adhere to our Code of Conduct.

**For developers:** Check out our documentation:
- [Development Guide](docs/development_guide.md) - Comprehensive development advice and lessons learned
- [Agent Development Guide](docs/agents.md) - Specific guidance for working with agents
- [Coding Standards](docs/CODING_STANDARDS.md) - Coding conventions and best practices

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| **1** | ✅ Complete | Core Infrastructure — Config loader, agent abstraction, file persistence |
| **2** | ✅ Complete | Orchestration — Dyadic/polyadic loops, feedback aggregation |
| **3** | 🚧 Partial | Convergence & Safeguards — Semantic convergence detection ✅, Devil's Advocate ❌ |
| **4** | 📋 Planned | Agent Memory System — Persistent, anti‑fragile memory (design complete) |
| **5** | 📋 Planned | Divergence Mode — Brainstorming and exploration workflows |
| **6** | 🚧 Partial | Metrics & Polish — Comprehensive testing ✅, metrics dashboard ❌ |

## FAQ

**Q: What kinds of artifacts can I use this for?**
A: Anything text-based! ADRs, unit tests, process documentation, Cursor rules, meeting templates—the tool is domain-agnostic. You can inject domain-specific "skill" prompts to guide the agents.

**Q: Do I need API keys for all the models I want to use?**
A: Yes. Vörs ting uses LiteLLM, so you need valid API keys for the providers (Anthropic, Google, OpenAI, etc.) you specify in your configuration. Set these as environment variables (e.g., `ANTHROPIC_API_KEY`).

**Q: What is "anti‑fragile memory"?**
A: It's our agent memory system that tracks agent performance over time. It learns from past successes, failures, and human feedback to dynamically improve the system—getting stronger from mistakes.

## Contact

For questions, support, or feedback, please use the [GitHub Issues](https://github.com/bdarlt/vors-ting/issues) page.
