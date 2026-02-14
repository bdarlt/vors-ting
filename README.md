# Vörs ting

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)

<!-- CI/CD Badges -->
[![CI Status](https://github.com/bdarlt/vors-ting/actions/workflows/ci.yml/badge.svg)](https://github.com/bdarlt/vors-ting/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badges/v2.json)](https://github.com/astral-sh/ruff)
[![Pyright](https://img.shields.io/badge/type--checked-pyright-blue)](https://github.com/microsoft/pyright)
[![pytest](https://img.shields.io/badge/tested_with-pytest-blue)](https://docs.pytest.org/)
[![Bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![McCabe](https://img.shields.io/badge/complexity-mccabe-orange)](https://github.com/PyCQA/mccabe)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://www.mkdocs.org/)

Vörs ting is a multi‑agent workflow tool for iterative feedback loops that drive convergent (and optionally divergent) refinement of work products. Inspired by the Norse goddess **Vör**, from whom nothing can be hidden, and the ancient ***ting*** assembly, it orchestrates AI agents to critique, debate, and improve artifacts until wisdom is reached.

## Table of Contents

- [Vörs ting](#vörs-ting)
  - [Table of Contents](#table-of-contents)
  - [Description](#description)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Basic Dyadic Pattern (Creator + Skeptic)](#basic-dyadic-pattern-creator--skeptic)
    - [Polyadic Pattern (Multiple Creators)](#polyadic-pattern-multiple-creators)
  - [Configuration](#configuration)
  - [Contributing](#contributing)
  - [License](#license)
  - [Roadmap](#roadmap)
  - [FAQ](#faq)
  - [Contact](#contact)

## Description

Vörs ting is a Python-based scaffolding that automates structured, multi-agent feedback loops. It helps you create higher-quality outputs—like ADRs, unit tests, or process docs—by systematically exposing work to adversarial and collaborative critique, iterating until a convergence of wisdom is achieved.

## Installation

**Prerequisites:** Python 3.10 or higher and `pip`.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/bdarlt/vors-ting.git
    cd vors-ting
    ```

2.  **Install the package and dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -e .
    ```

## Usage

Vörs ting is controlled via a command-line interface (CLI) using a YAML configuration file.

### Basic Dyadic Pattern (Creator + Skeptic)

1.  Create a configuration file, e.g., `my_review.yaml`.
2.  Run the tool:
    ```bash
    vors run my_review.yaml
    ```

### Polyadic Pattern (Multiple Creators)

To have multiple agents create and review each other's work, define them all as `creator` in your config. The orchestrator will automatically handle the peer review rounds.

For detailed examples, see the `examples/` directory in this repository.

## Configuration

The tool is configured via a YAML file. Below is a minimal example. For a full reference of all options (rubrics, safeguards, divergence mode, etc.), please see the [Configuration Guide](docs/configuration.md).

```yaml
task: "Write an ADR for migrating from REST to GraphQL"
artifact_type: "adr"
agents:
  - name: "Creator1"
    role: "creator"
    model: "claude-3-opus-20240229"
    provider: "anthropic"
  - name: "Skeptic"
    role: "reviewer"
    model: "gemini-1.5-pro"
    provider: "google"
rounds: 5
mode: "converge"
```

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
