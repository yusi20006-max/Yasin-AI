"""CLI for runtime-configured OpenAI-compatible providers."""
from __future__ import annotations

import argparse
import getpass
import json
import sys
from typing import Any

from yasinai.contracts import GenerationRequest as PublicGenerationRequest
from yasinai.providers.base import ProviderError
from yasinai.providers.config_store import ProviderConfigError, ProviderStore, validate_base_url
from yasinai.providers.generic_openai import GenericOpenAIProvider


def _build_provider(config: dict[str, str], transport: Any = None) -> GenericOpenAIProvider:
    return GenericOpenAIProvider(
        name=config["name"],
        base_url=config["base_url"],
        api_key=config["api_key"],
        default_model=config["model"],
        transport=transport,
    )


def _test_provider(config: dict[str, str]) -> None:
    provider = _build_provider(config)
    request = PublicGenerationRequest(prompt="Reply with exactly: YASIN_OK", model=config["model"], max_tokens=8, temperature=0.0)
    provider.generate(request)


def _prompt_setup(existing: dict[str, str] | None = None) -> dict[str, str]:
    existing = existing or {}
    name = input(f"Provider name [{existing.get('name', '')}]: ").strip() or existing.get("name", "")
    base_url = input(f"Base URL [{existing.get('base_url', '')}]: ").strip() or existing.get("base_url", "")
    model = input(f"Model [{existing.get('model', '')}]: ").strip() or existing.get("model", "")
    key = getpass.getpass("API Key (hidden): ")
    if not key and existing:
        key = existing["api_key"]
    return {"name": name, "base_url": base_url, "model": model, "api_key": key}


def handle_setup(args: argparse.Namespace) -> int:
    store = ProviderStore()
    try:
        current = store.get(args.name) if args.name else None
        config = _prompt_setup(current)
        validate_base_url(config["base_url"])
        print("Testing provider connection...")
        _test_provider(config)
        store.save(**config, make_default=bool(args.default))
        print(f"SUCCESS: provider '{config['name']}' configured and tested.")
        return 0
    except (ProviderConfigError, ProviderError, ValueError, OSError) as exc:
        print(f"Provider setup failed: {exc}", file=sys.stderr)
        return 1


def handle_list(args: argparse.Namespace) -> int:
    try:
        rows = ProviderStore().list()
        if args.json:
            print(json.dumps(rows, indent=2))
            return 0
        if not rows:
            print("No providers configured.")
            return 0
        for item in rows:
            marker = "*" if item["default"] else " "
            print(f"{marker} {item['name']}  {item['model']}  {item['base_url']}")
        return 0
    except ProviderConfigError as exc:
        print(f"Provider list failed: {exc}", file=sys.stderr)
        return 1


def handle_use(args: argparse.Namespace) -> int:
    try:
        ProviderStore().use(args.name)
        print(f"Default provider: {args.name}")
        return 0
    except ProviderConfigError as exc:
        print(f"Provider selection failed: {exc}", file=sys.stderr)
        return 1


def handle_remove(args: argparse.Namespace) -> int:
    try:
        removed = ProviderStore().remove(args.name)
        if not removed:
            print(f"Provider '{args.name}' is not configured.", file=sys.stderr)
            return 1
        print(f"Removed provider '{args.name}'.")
        return 0
    except ProviderConfigError as exc:
        print(f"Provider removal failed: {exc}", file=sys.stderr)
        return 1


def handle_test(args: argparse.Namespace) -> int:
    try:
        config = ProviderStore().get(args.name) if args.name else ProviderStore().default()
        if not config:
            print("No provider is configured.", file=sys.stderr)
            return 1
        print(f"Testing provider '{config['name']}'...")
        _test_provider(config)
        print("SUCCESS: provider connection and model test passed.")
        return 0
    except (ProviderConfigError, ProviderError, ValueError, OSError) as exc:
        print(f"Provider test failed: {exc}", file=sys.stderr)
        return 1


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="yasin provider", description="Manage runtime-configured AI providers")
    sub = parser.add_subparsers(dest="action")

    setup = sub.add_parser("setup", help="Add or update a provider")
    setup.add_argument("name", nargs="?", help="Existing provider name to update")
    setup.add_argument("--default", action="store_true", help="Make this provider the default")
    setup.set_defaults(func=handle_setup)

    listing = sub.add_parser("list", help="List configured providers")
    listing.add_argument("--json", action="store_true")
    listing.set_defaults(func=handle_list)

    use = sub.add_parser("use", help="Select the default provider")
    use.add_argument("name")
    use.set_defaults(func=handle_use)

    test = sub.add_parser("test", help="Test a configured provider")
    test.add_argument("name", nargs="?")
    test.set_defaults(func=handle_test)

    remove = sub.add_parser("remove", help="Remove a configured provider")
    remove.add_argument("name")
    remove.set_defaults(func=handle_remove)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    if not getattr(args, "action", None):
        parser.print_help()
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
