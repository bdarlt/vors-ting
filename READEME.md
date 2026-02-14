# Vörs ting

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
<!-- Add other badges here as your project matures, e.g., build status, test coverage -->

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
