#!/usr/bin/env python3
"""
Interactive CLI for Worker System Agent
========================================

Provides a REPL interface for continuous interaction with the system agent.
Handles confirmations for dangerous operations and maintains conversation context.

Usage:
    python cli.py

    Or make executable:
    chmod +x cli.py
    ./cli.py
"""

import os
import sys
from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.file import FileTools
from agno.tools.package_manager import PackageManagerTools
from agno.tools.shell import ShellTools
from agno.tools.system_monitor import SystemMonitorTools


def create_agent() -> Agent:
    """Create and configure the system agent."""
    instructions = """\
You are a System Administrator Assistant for a RISC-V Linux system.

Help users manage and monitor their Linux system through natural language.
Always explain what you're doing, confirm destructive operations, and provide
clear, concise responses.

Keep responses focused and technical. Use tables or structured output when
showing multiple items. No emojis.
"""

    return Agent(
        name="Worker System Assistant",
        model=OpenAIResponses(id="gpt-5.5"),
        instructions=instructions,
        tools=[
            SystemMonitorTools(),
            ShellTools(
                base_dir="/home/bianbu/agno-riscv64",
                requires_confirmation_tools=["run_shell_command"]
            ),
            FileTools(
                base_dir=Path("/home/bianbu/agno-riscv64"),
                enable_delete_file=True,
                all=True,
            ),
            PackageManagerTools(
                requires_confirmation_tools=[
                    "install_package",
                    "remove_package",
                    "upgrade_packages",
                ]
            ),
        ],
        markdown=True,
        show_tool_calls=True,
        add_datetime_to_context=True,
    )


def print_welcome():
    """Print welcome message."""
    print("\n" + "=" * 70)
    print("  Worker System Agent - AI System Administrator")
    print("=" * 70)
    print("\nType your commands in natural language. Examples:")
    print("  - Check system health")
    print("  - List top 5 processes by memory")
    print("  - Show disk space")
    print("  - Find all Python files")
    print("\nCommands: 'exit', 'quit', 'bye' to quit | 'clear' to clear screen")
    print("=" * 70 + "\n")


def handle_confirmations(run_response) -> bool:
    """Handle confirmation prompts for dangerous operations.

    Returns:
        bool: True if should continue with response, False if cancelled
    """
    if not run_response.active_requirements:
        return True

    print("\n" + "-" * 70)
    print("CONFIRMATION REQUIRED")
    print("-" * 70)

    for requirement in run_response.active_requirements:
        if requirement.needs_confirmation:
            tool = requirement.tool_execution
            print(f"\nTool: {tool.tool_name}")
            print(f"Args: {tool.tool_args}")
            print()

            while True:
                answer = input("Approve this action? [y/N]: ").strip().lower()
                if answer in ['y', 'yes']:
                    requirement.confirm()
                    print("✓ Approved")
                    break
                elif answer in ['n', 'no', '']:
                    requirement.reject()
                    print("✗ Rejected")
                    return False
                else:
                    print("Please answer 'y' or 'n'")

    print("-" * 70 + "\n")
    return True


def run_repl():
    """Run the interactive REPL loop."""
    print_welcome()

    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ WARNING: OPENAI_API_KEY not set in environment")
        print("Set it with: export OPENAI_API_KEY='your-key-here'\n")
        return

    # Create agent
    try:
        agent = create_agent()
    except Exception as e:
        print(f"Error creating agent: {e}")
        return

    print("Agent ready. Type your command:\n")

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\nGoodbye!")
                break

            if user_input.lower() == 'clear':
                os.system('clear' if os.name != 'nt' else 'cls')
                print_welcome()
                continue

            # Run agent
            print("\nAgent: ", end="", flush=True)
            run_response = agent.run(user_input)

            # Handle confirmations
            if run_response.active_requirements:
                if handle_confirmations(run_response):
                    # Continue with approved actions
                    run_response = agent.continue_run(
                        run_response,
                        requirements=run_response.requirements
                    )
                    print("\nAgent: ", end="", flush=True)
                    print(run_response.content)
                else:
                    print("\nAction cancelled by user.")
            else:
                print(run_response.content)

            print()

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' to quit or continue with another command.\n")
            continue
        except EOFError:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\n\nError: {e}")
            print("Please try again.\n")
            continue


def main():
    """Main entry point."""
    try:
        run_repl()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
