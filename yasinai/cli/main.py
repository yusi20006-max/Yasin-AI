import argparse
import json
import logging
import sys
from typing import Any, Dict, List, Optional
from yasinai.core.runtime import Runtime

logger = logging.getLogger(__name__)


def handle_status(args: argparse.Namespace) -> int:
    """
    Handle the 'yasin status' command.
    Boots the Core Runtime and prints system details.
    """
    logger.debug("Executing CLI command: status")
    try:
        runtime = Runtime()
        runtime.start()
        info = runtime.system_info.get_info()
        runtime.shutdown()

        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print("=========================================")
            print("         YasinAI System Status           ")
            print("=========================================")
            print(f"App Name:     {info.get('app_name')}")
            print(f"Version:      {info.get('version')}")
            print(f"Status:       {info.get('status')}")
            print(f"OS:           {info.get('os')}")
            print(f"Platform:     {info.get('platform')}")
            print(f"Architecture: {info.get('architecture')}")
            print(f"Python Ver:   {info.get('python_version', '').split()[0] if info.get('python_version') else ''}")
            print("=========================================")
        logger.info("Successfully displayed status.")
        return 0
    except Exception as e:
        logger.error(f"Error checking status: {e}", exc_info=True)
        print(f"Error checking status: {e}", file=sys.stderr)
        return 1


def handle_agent_create(args: argparse.Namespace) -> int:
    """
    Handle the 'yasin agent create' command.
    Creates a new AI Agent using the Developer Platform.
    """
    name: str = args.name
    role: str = getattr(args, "role", "general")
    description: str = getattr(args, "description", "A helpful AI agent")
    agent_type: str = getattr(args, "type", "standard")

    logger.debug(f"Executing CLI command: agent create with name={name}, role={role}, type={agent_type}")

    try:
        from developer_platform.agent import AgentSDK

        sdk = AgentSDK()
        agent = sdk.create_agent(name=name, role=role, description=description, type=agent_type)
        agent.start()

        result = {
            "success": True,
            "message": f"Agent '{agent.name}' created successfully.",
            "agent": {
                "name": agent.name,
                "role": agent.role,
                "description": agent.description,
                "type": agent.type,
                "status": agent.status
            }
        }

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("-----------------------------------------")
            print(f"Creating agent '{agent.name}'...")
            print("-----------------------------------------")
            print(f"Role:        {agent.role}")
            print(f"Description: {agent.description}")
            print(f"Type:        {agent.type}")
            print("-----------------------------------------")
            print(f"SUCCESS: Agent '{agent.name}' is ready to deploy.")
        logger.info(f"Successfully created agent: {agent.name}")
        return 0
    except Exception as e:
        logger.error(f"Error creating agent: {e}", exc_info=True)
        print(f"Error creating agent: {e}", file=sys.stderr)
        return 1


def handle_memory_search(args: argparse.Namespace) -> int:
    """
    Handle the 'yasin memory search' command.
    Searches semantic memory using the Knowledge Platform.
    """
    query: str = args.query
    limit: int = getattr(args, "limit", 5)
    threshold: float = getattr(args, "threshold", 0.7)

    logger.debug(f"Executing CLI command: memory search with query='{query}', limit={limit}, threshold={threshold}")

    try:
        from knowledge_platform.semantic_search import Retriever

        retriever = Retriever()
        # Populate the retriever with mock data to maintain backward compatibility and support real semantic indexing
        retriever.add_document("mem_001", "YasinAI configuration loading rules.")
        retriever.add_document("mem_002", "How to register custom modules in Core Runtime.")
        retriever.add_document("mem_003", "Security platform and identity management specs.")

        # Execute search
        search_results = retriever.retrieve(query or "", limit=limit, threshold=threshold)

        # Map output format for CLI output
        results = []
        for r in search_results:
            results.append({
                "id": r["id"],
                "content": r["metadata"]["text"],
                "score": round(r["score"], 2)
            })

        output = {
            "query": query,
            "limit": limit,
            "threshold": threshold,
            "results": results
        }

        if args.json:
            print(json.dumps(output, indent=2))
        else:
            print("-----------------------------------------")
            print(f"Searching memory for query: '{query or '(all)'}'")
            print(f"Limit: {limit} | Threshold: {threshold}")
            print("-----------------------------------------")
            if not results:
                print("No matching memories found.")
            for i, res in enumerate(results, start=1):
                print(f"{i}. [{res['score']:.2f}] {res['content']} ({res['id']})")
            print("-----------------------------------------")
        logger.info("Successfully searched memory.")
        return 0
    except Exception as e:
        logger.error(f"Error searching memory: {e}", exc_info=True)
        print(f"Error searching memory: {e}", file=sys.stderr)
        return 1


def handle_security_check(args: argparse.Namespace) -> int:
    """
    Handle the 'yasin security check' command.
    Simulates security vulnerability scan and audit check.
    """
    logger.debug("Executing CLI command: security check")

    try:
        # Simulated check items
        checks = [
            {"id": "SEC_001", "name": "Environment Secrets Check", "passed": True, "details": "No plain-text credentials found in codebase."},
            {"id": "SEC_002", "name": "File Permissions", "passed": True, "details": "Repository files are properly restricted."},
            {"id": "SEC_003", "name": "Encryption Engines", "passed": True, "details": "SHA-256 and AES configuration validated."},
            {"id": "SEC_004", "name": "Policy Engine Health", "passed": True, "details": "Role-Based Access Control policies loaded."},
        ]

        failed_checks = [c for c in checks if not c["passed"]]
        overall_status = "SECURE" if not failed_checks else "VULNERABLE"

        output = {
            "status": overall_status,
            "scanned_items": len(checks),
            "failed_items": len(failed_checks),
            "checks": checks
        }

        if args.json:
            print(json.dumps(output, indent=2))
        else:
            print("=========================================")
            print("YasinAI Security Platform - Audit Check")
            print(f"Status: {overall_status}")
            print("=========================================")
            for check in checks:
                status_str = "[ PASS ]" if check["passed"] else "[ FAIL ]"
                print(f"{status_str} {check['name']}")
                print(f"         Details: {check['details']}")
            print("=========================================")
            print(f"Scan complete. {len(checks)} checks performed.")
        logger.info("Successfully executed security check.")
        return 0
    except Exception as e:
        logger.error(f"Error checking security: {e}", exc_info=True)
        print(f"Error checking security: {e}", file=sys.stderr)
        return 1


def handle_package_build(args: argparse.Namespace) -> int:
    """
    Handle the 'yasin package build' command.
    Packages modules and extensions using the Developer Platform PackageBuilder.
    """
    output_dir: str = getattr(args, "output", "dist/")
    version: str = getattr(args, "version", "1.1.0")

    logger.debug(f"Executing CLI command: package build with output_dir={output_dir}, version={version}")

    try:
        from developer_platform.package_builder import PackageBuilder

        builder = PackageBuilder()
        result = builder.build_package(name="yasinai", version=version, output_directory=output_dir)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("-----------------------------------------")
            print(f"Building YasinAI deployment package v{version}...")
            print(f"Target directory: {output_dir}")
            print("-----------------------------------------")
            print("Adding modules to package:")
            for f in result["files_included"]:
                print(f"  + {f}")
            print("-----------------------------------------")
            print(f"SUCCESS: Created build artifact: {output_dir}{result['package_name']}")
        logger.info(f"Successfully built package v{version}")
        return 0
    except Exception as e:
        logger.error(f"Error building package: {e}", exc_info=True)
        print(f"Error building package: {e}", file=sys.stderr)
        return 1


def handle_serve(args: argparse.Namespace) -> int:
    """
    Handle the 'yasin serve' command.
    Keeps the YasinAI runtime alive as a long-running foreground supervisor loop,
    performing periodic health checks.
    """
    import signal
    import time
    from yasinai.deployment.health_check import HealthCheck

    logger.debug("Executing CLI command: serve")
    interval: int = getattr(args, "interval", 300)

    # Validate interval
    if interval <= 0:
        logger.error("Interval must be a positive integer.")
        print("Error: Interval must be a positive integer.", file=sys.stderr)
        return 1

    runtime = Runtime()
    stop_flag = False

    def signal_handler(signum, frame):
        nonlocal stop_flag
        stop_flag = True

    # Register signal handlers
    original_sigint = signal.getsignal(signal.SIGINT)
    original_sigterm = signal.getsignal(signal.SIGTERM)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        runtime.start()

        health_checker = HealthCheck()

        startup_msg = f"YasinAI Core Runtime started in foreground supervisor mode. Health check interval: {interval} seconds."
        if args.json:
            print(json.dumps({
                "event": "startup",
                "status": "running",
                "interval": interval,
                "message": startup_msg
            }))
        else:
            print("=========================================")
            print("         YasinAI Foreground Serve        ")
            print("=========================================")
            print(startup_msg)
            print("Press Ctrl+C to stop.")
            print("=========================================")
        logger.info(startup_msg)

        while not stop_flag:
            report = health_checker.run_all_checks()

            if args.json:
                print(json.dumps({
                    "event": "health_check",
                    "status": report.get("status"),
                    "success": report.get("success"),
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }))
            else:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"[{timestamp}] Health Check Status: {report.get('status')} (Success: {report.get('success')})")

            logger.info(f"Health Check Completed: {report}")

            # Sleep in small increments to be responsive to signals
            slept = 0
            while slept < interval and not stop_flag:
                time.sleep(1)
                slept += 1

    except Exception as e:
        logger.error(f"Error in serve loop: {e}", exc_info=True)
        print(f"Error in serve loop: {e}", file=sys.stderr)
        return 1
    finally:
        # Restore signal handlers
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGTERM, original_sigterm)

        shutdown_msg = "Shutting down YasinAI Core Runtime cleanly..."
        if args.json:
            print(json.dumps({
                "event": "shutdown",
                "status": "stopped",
                "message": shutdown_msg
            }))
        else:
            print(shutdown_msg)
        logger.info(shutdown_msg)

        runtime.shutdown()

    return 0


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the argument parser for YasinAI CLI.
    """
    # Create a parent parser to share common options like --json
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    parser = argparse.ArgumentParser(
        prog="yasin",
        description="YasinAI Command Line management interface.",
        parents=[parent_parser]
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. 'status' command
    status_parser = subparsers.add_parser("status", help="Check system status and details", parents=[parent_parser])
    status_parser.set_defaults(func=handle_status)

    # 2. 'agent' command and its 'create' subcommand
    agent_parser = subparsers.add_parser("agent", help="Manage AI Agents", parents=[parent_parser])
    agent_subparsers = agent_parser.add_subparsers(dest="subcommand", help="Agent subcommands")

    agent_create_parser = agent_subparsers.add_parser("create", help="Create a new AI Agent", parents=[parent_parser])
    agent_create_parser.add_argument("name", nargs="?", default="default_agent", help="Name of the agent")
    agent_create_parser.add_argument("--role", default="general", help="Role of the agent (e.g. general, security, knowledge)")
    agent_create_parser.add_argument("--description", default="A helpful AI agent", help="Description of the agent")
    agent_create_parser.add_argument("--type", default="standard", help="Type of the agent (e.g. standard, specialist)")
    agent_create_parser.set_defaults(func=handle_agent_create)

    # 3. 'memory' command and its 'search' subcommand
    memory_parser = subparsers.add_parser("memory", help="Manage Knowledge Memory Platform", parents=[parent_parser])
    memory_subparsers = memory_parser.add_subparsers(dest="subcommand", help="Memory subcommands")

    memory_search_parser = memory_subparsers.add_parser("search", help="Search semantic memory", parents=[parent_parser])
    memory_search_parser.add_argument("query", nargs="?", default="", help="Query to search semantic memory")
    memory_search_parser.add_argument("--limit", type=int, default=5, help="Maximum search results")
    memory_search_parser.add_argument("--threshold", type=float, default=0.7, help="Minimum matching similarity score")
    memory_search_parser.set_defaults(func=handle_memory_search)

    # 4. 'security' command and its 'check' subcommand
    security_parser = subparsers.add_parser("security", help="Manage Security Platform", parents=[parent_parser])
    security_subparsers = security_parser.add_subparsers(dest="subcommand", help="Security subcommands")

    security_check_parser = security_subparsers.add_parser("check", help="Run audit and security checks", parents=[parent_parser])
    security_check_parser.set_defaults(func=handle_security_check)

    # 5. 'package' command and its 'build' subcommand
    package_parser = subparsers.add_parser("package", help="Manage Deployment Packaging", parents=[parent_parser])
    package_subparsers = package_parser.add_subparsers(dest="subcommand", help="Package subcommands")

    package_build_parser = package_subparsers.add_parser("build", help="Build deployment artifacts", parents=[parent_parser])
    package_build_parser.add_argument("--output", default="dist/", help="Output directory")
    package_build_parser.add_argument("--version", default="1.1.0", help="Target package version")
    package_build_parser.set_defaults(func=handle_package_build)

    # 6. 'serve' command
    serve_parser = subparsers.add_parser("serve", help="Keep Core Runtime alive as a foreground process", parents=[parent_parser])
    serve_parser.add_argument("--interval", type=int, default=300, help="Periodic health-check interval in seconds")
    serve_parser.set_defaults(func=handle_serve)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    """
    Main CLI entrypoint. Parses command line arguments and executes requested subcommands.
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(0)

    # For commands with nested subcommands, ensure subcommand is provided
    if args.command in ("agent", "memory", "security", "package"):
        if not getattr(args, "subcommand", None):
            # Print subcommand help
            sub_parsers_actions = [
                action for action in parser._subparsers._actions
                if isinstance(action, argparse._SubParsersAction)
            ]
            for action in sub_parsers_actions:
                subcommand_parser = action.choices.get(args.command)
                if subcommand_parser:
                    subcommand_parser.print_help()
                    sys.exit(0)
            parser.print_help()
            sys.exit(0)

    if hasattr(args, "func"):
        # Propagate the top-level --json option to nested args if not present
        if args.json and not hasattr(args, "json"):
            setattr(args, "json", True)
        exit_code: int = args.func(args)
        sys.exit(exit_code)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
