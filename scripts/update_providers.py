#!/usr/bin/env python3
"""Update and maintain LiteLLM provider metadata.

This script can:
1. Fetch latest provider info from LiteLLM docs (if available)
2. Add/update a provider manually via CLI
3. Validate the providers.yaml file
4. List all providers with their required env vars

Usage:
    uv run python scripts/update_providers.py list
    uv run python scripts/update_providers.py add mistral --api-key MISTRAL_API_KEY
    uv run python scripts/update_providers.py validate
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

PROVIDERS_FILE = Path(__file__).parent.parent / "providers.yaml"


def load_providers() -> dict[str, Any]:
    """Load providers from YAML file."""
    if not PROVIDERS_FILE.exists():
        return {"providers": {}, "defaults": {}}

    with PROVIDERS_FILE.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"providers": {}, "defaults": {}}


def save_providers(data: dict[str, Any]) -> None:
    """Save providers to YAML file with comments."""
    data["last_updated"] = datetime.now(tz=UTC).strftime("%Y-%m-%d")

    with PROVIDERS_FILE.open("w", encoding="utf-8") as f:
        f.write("# LiteLLM Provider Configuration\n")
        f.write(
            "# Auto-generated metadata for LLM provider "
            "validation and documentation\n"
        )
        f.write(f"# Last updated: {data['last_updated']}\n\n")

        # Write providers section
        f.write("providers:\n")
        for name, config in data.get("providers", {}).items():
            f.write(f"  # {config.get('name', name)}\n")
            f.write(f"  {name}:\n")
            display_name = config.get("name", name)
            f.write(f'    name: "{display_name}"\n')
            api_key_val = format_yaml_value(config.get("api_key_env"))
            f.write(f"    api_key_env: {api_key_val}\n")
            base_url_val = format_yaml_value(config.get("base_url_env"))
            f.write(f"    base_url_env: {base_url_val}\n")
            f.write("    temperature:\n")
            temp = config.get("temperature", {"min": 0.0, "max": 2.0})
            f.write(f"      min: {temp.get('min', 0.0)}\n")
            f.write(f"      max: {temp.get('max', 2.0)}\n")
            docs_url = config.get("docs_url", "")
            f.write(f'    docs_url: "{docs_url}"\n')
            supports_str = config.get("supports_streaming", True)
            f.write(f"    supports_streaming: {supports_str}\n")
            notes = config.get("notes", "")
            f.write(f'    notes: "{notes}"\n')
            f.write("\n")

        # Write defaults
        f.write("# Default values for unknown providers\n")
        f.write("defaults:\n")
        defaults = data.get("defaults", {})
        temp_defaults = defaults.get("temperature", {"min": 0.0, "max": 2.0})
        f.write("  temperature:\n")
        f.write(f"    min: {temp_defaults.get('min', 0.0)}\n")
        f.write(f"    max: {temp_defaults.get('max', 2.0)}\n")
        default_key = defaults.get("api_key_env", "{PROVIDER}_API_KEY}")
        f.write(f'  api_key_env: "{default_key}"\n')
        f.write(f"  base_url_env: {format_yaml_value(defaults.get('base_url_env'))}\n")


def format_yaml_value(value: Any) -> str:
    """Format a value for YAML output."""
    if value is None:
        return "null"
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def cmd_list(args: argparse.Namespace) -> int:  # noqa: ARG001
    """List all providers with their API key env vars."""
    data = load_providers()
    providers = data.get("providers", {})

    print(  # noqa: T201
        f"\n{'Provider':<20} {'API Key Env Var':<30} "
        f"{'Temperature':<15} {'Base URL Env':<30}"
    )
    print("=" * 95)  # noqa: T201

    for name, config in sorted(providers.items()):
        api_key = config.get("api_key_env", "N/A")
        temp = config.get("temperature", {})
        temp_range = f"{temp.get('min', 0)}-{temp.get('max', 2)}"
        base_url = config.get("base_url_env") or "N/A"
        print(  # noqa: T201
            f"{name:<20} {api_key:<30} {temp_range:<15} {base_url:<30}"
        )

    print()  # noqa: T201
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add or update a provider."""
    data = load_providers()
    providers = data.get("providers", {})

    name = args.name.lower()

    # Build config from args
    config: dict[str, Any] = {
        "name": args.display_name or args.name.title(),
        "api_key_env": args.api_key,
        "base_url_env": args.base_url,
        "temperature": {
            "min": args.temp_min,
            "max": args.temp_max,
        },
        "docs_url": args.docs_url or f"https://docs.litellm.ai/docs/providers/{name}",
        "supports_streaming": not args.no_streaming,
        "notes": args.notes or "",
    }

    # Remove None values for cleaner output
    if args.base_url is None:
        config["base_url_env"] = None

    providers[name] = config
    data["providers"] = providers

    save_providers(data)
    print(f"Added/updated provider: {name}")  # noqa: T201
    return 0


def cmd_validate(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Validate the providers.yaml file."""
    data = load_providers()
    providers = data.get("providers", {})
    errors = []

    for name, config in providers.items():
        # Check required fields
        if "api_key_env" not in config:
            errors.append(f"{name}: missing api_key_env")
        if "temperature" not in config:
            errors.append(f"{name}: missing temperature")
        else:
            temp = config["temperature"]
            if "min" not in temp or "max" not in temp:
                errors.append(f"{name}: temperature missing min/max")
            elif temp["min"] >= temp["max"]:
                errors.append(f"{name}: temperature min >= max")
            elif temp["min"] < 0:
                errors.append(f"{name}: temperature min < 0")
            elif temp["max"] > 5:  # noqa: PLR2004
                errors.append(f"{name}: temperature max > 5 (unusual)")

    if errors:
        print("Validation errors:")  # noqa: T201
        for error in errors:
            print(f"  - {error}")  # noqa: T201
        return 1

    print(  # noqa: T201
        f"OK: Validation passed. {len(providers)} providers configured."
    )
    return 0


def cmd_check_env(args: argparse.Namespace) -> int:  # noqa: ARG001
    """Check which API keys are set in environment."""
    import os  # noqa: PLC0415

    data = load_providers()
    providers = data.get("providers", {})

    print(  # noqa: T201
        f"\n{'Provider':<20} {'API Key Env Var':<30} {'Status':<10}"
    )
    print("=" * 70)  # noqa: T201

    missing = []
    for name, config in sorted(providers.items()):
        api_key_env = config.get("api_key_env")
        if api_key_env:
            is_set = api_key_env in os.environ
            status = "Set" if is_set else "Missing"
            print(  # noqa: T201
                f"{name:<20} {api_key_env:<30} {status:<10}"
            )
            if not is_set:
                missing.append((name, api_key_env))

    print()  # noqa: T201
    if missing:
        print(f"Missing {len(missing)} API key(s):")  # noqa: T201
        for name, key in missing:
            print(f"  - {name}: {key}")  # noqa: T201
    else:
        print("All configured provider API keys are set!")  # noqa: T201

    print()  # noqa: T201
    return 0 if not missing else 1


def main() -> int:
    """Run the CLI."""
    parser = argparse.ArgumentParser(
        description="Manage LiteLLM provider metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list                           # List all providers
  %(prog)s check-env                      # Check API keys in environment
  %(prog)s add mistral --api-key MISTRAL_API_KEY --temp-max 1.0
  %(prog)s validate                       # Validate providers.yaml
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    subparsers.add_parser("list", help="List all providers")

    # check-env command
    subparsers.add_parser("check-env", help="Check environment variables")

    # add command
    add_parser = subparsers.add_parser("add", help="Add or update a provider")
    add_parser.add_argument("name", help="Provider key name (lowercase)")
    add_parser.add_argument(
        "--api-key", required=True, help="API key environment variable"
    )
    add_parser.add_argument(
        "--base-url", help="Base URL environment variable (optional)"
    )
    add_parser.add_argument("--display-name", help="Human-readable name")
    add_parser.add_argument(
        "--temp-min", type=float, default=0.0, help="Min temperature"
    )
    add_parser.add_argument(
        "--temp-max", type=float, default=2.0, help="Max temperature"
    )
    add_parser.add_argument("--docs-url", help="Documentation URL")
    add_parser.add_argument(
        "--no-streaming", action="store_true",
        help="Does not support streaming"
    )
    add_parser.add_argument("--notes", help="Additional notes")

    # validate command
    subparsers.add_parser("validate", help="Validate providers.yaml")

    args = parser.parse_args()

    commands = {
        "list": cmd_list,
        "add": cmd_add,
        "validate": cmd_validate,
        "check-env": cmd_check_env,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
