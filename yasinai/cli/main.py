"""Command Line Interface (CLI) for YasinAI."""

import argparse
import sys
from yasinai.core.runtime import RuntimeOrchestrator


def handle_status(args) -> int:
    """Handle 'yasin status' command."""
    print("YasinAI System Status:")
    orchestrator = RuntimeOrchestrator()
    orchestrator.startup()
    print(f"  Core State: {orchestrator.state}")
    print(f"  Version: {orchestrator.system_info.version}")
    print(f"  Platform: {orchestrator.system_info.platform}")
    print(f"  Python Version: {orchestrator.system_info.python_version.split()[0]}")
    orchestrator.shutdown()
    return 0


def handle_agent(args) -> int:
    """Handle 'yasin agent' commands."""
    if args.agent_cmd == "create":
        print(f"Creating agent '{args.name}'...")
        # Placeholder for Developer Platform integration
        return 0
    else:
        print("Error: Unknown agent subcommand.", file=sys.stderr)
        return 1


def handle_memory(args) -> int:
    """Handle 'yasin memory' commands."""
    if args.memory_cmd == "search":
        print(f"Searching memory for '{args.query}'...")
        # Placeholder for Knowledge Platform integration
        return 0
    else:
        print("Error: Unknown memory subcommand.", file=sys.stderr)
        return 1


def handle_security(args) -> int:
    """Handle 'yasin security' commands."""
    if args.security_cmd == "check":
        print("Running security check...")
        # Placeholder for Security Platform integration
        return 0
    else:
        print("Error: Unknown security subcommand.", file=sys.stderr)
        return 1


def handle_package(args) -> int:
    """Handle 'yasin package' commands."""
    if args.package_cmd == "build":
        path = args.path or "."
        print(f"Building package at '{path}'...")
        # Placeholder for Developer Platform/Deployment integration
        return 0
    else:
        print("Error: Unknown package subcommand.", file=sys.stderr)
        return 1


def main(argv=None) -> int:
    """Main CLI entry point."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        prog="yasin",
        description="YasinAI Command-Line Management Interface"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Status command
    subparsers.add_parser("status", help="Show system status")

    # Agent commands
    agent_parser = subparsers.add_parser("agent", help="Manage agents")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_cmd", required=True)
    agent_create_parser = agent_subparsers.add_parser("create", help="Create a new agent")
    agent_create_parser.add_argument("name", help="Name of the agent to create")

    # Memory commands
    memory_parser = subparsers.add_parser("memory", help="Manage memory and knowledge")
    memory_subparsers = memory_parser.add_subparsers(dest="memory_cmd", required=True)
    memory_search_parser = memory_subparsers.add_parser("search", help="Search memory")
    memory_search_parser.add_argument("query", help="Query string to search for")

    # Security commands
    security_parser = subparsers.add_parser("security", help="Manage security audits")
    security_subparsers = security_parser.add_subparsers(dest="security_cmd", required=True)
    security_subparsers.add_parser("check", help="Run a security validation check")

    # Package commands
    package_parser = subparsers.add_parser("package", help="Manage developer packages")
    package_subparsers = package_parser.add_subparsers(dest="package_cmd", required=True)
    package_build_parser = package_subparsers.add_parser("build", help="Build a developer package")
    package_build_parser.add_argument("path", nargs="?", default=".", help="Path to build package from (default: current directory)")

    # Parse arguments
    args = parser.parse_args(argv)

    if args.command == "status":
        return handle_status(args)
    elif args.command == "agent":
        return handle_agent(args)
    elif args.command == "memory":
        return handle_memory(args)
    elif args.command == "security":
        return handle_security(args)
    elif args.command == "package":
        return handle_package(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
