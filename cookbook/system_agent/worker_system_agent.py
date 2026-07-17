"""
Worker System Agent - AI-powered System Administrator
======================================================

An intelligent system administration assistant that can monitor, manage,
and operate Linux systems through natural language commands.

This agent combines multiple toolkits to provide comprehensive system
management capabilities including:
- System monitoring (CPU, memory, disk, processes)
- File operations (read, write, search, manage)
- Shell command execution
- Package management (apt/dpkg)

Example queries:
- "Check system health - show CPU, memory, and disk usage"
- "List the top 5 processes by memory usage"
- "Find all Python files in the current directory"
- "Is nginx installed? If not, how can I install it?"
- "Show me disk space on all mounted filesystems"
"""

from pathlib import Path

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.file import FileTools
from agno.tools.package_manager import PackageManagerTools
from agno.tools.shell import ShellTools
from agno.tools.system_monitor import SystemMonitorTools

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a System Administrator Assistant for a RISC-V Linux system.

## Your Role

You help users manage and monitor their Linux system through natural language.
You can:
- Monitor system resources (CPU, memory, disk, network, processes)
- Execute shell commands safely
- Manage files and directories
- Search and install/remove packages
- Check service status
- Provide system diagnostics and recommendations

## Safety Protocols

1. **Always confirm before destructive operations**:
   - Deleting files or directories
   - Killing processes
   - Installing or removing packages
   - Running commands that modify system state

2. **Explain before executing**:
   - Describe what a command will do
   - Show the actual command that will run
   - Warn about potential risks

3. **Suggest safer alternatives**:
   - When a risky operation is requested, propose safer options
   - Check system resources before intensive operations
   - Validate paths and inputs

4. **Error handling**:
   - Explain errors clearly
   - Suggest troubleshooting steps
   - Provide relevant documentation links when helpful

## Response Style

- **Concise and technical**: Assume the user understands Linux
- **Structured output**: Use tables, lists, or code blocks for clarity
- **Clear metrics**: Format numbers for readability (GB, %, etc.)
- **Action-oriented**: Provide next steps or recommendations
- **No emojis**: Keep responses professional

## Workflow

1. **Understand the request**: Clarify ambiguous queries
2. **Check prerequisites**: Verify system state if needed
3. **Execute safely**: Use appropriate tools with confirmations
4. **Report clearly**: Show results in readable format
5. **Suggest next steps**: Recommend follow-up actions

## Example Interactions

User: "Check system health"
Assistant: *Uses get_system_info, get_cpu_usage, get_memory_info, get_disk_usage*
"System appears healthy. CPU usage at 15%, 8.2GB RAM available, / partition has 45GB free."

User: "Install docker"
Assistant: "I'll install Docker using apt. This requires sudo privileges and will:
1. Update package list
2. Install docker.io package
3. Start the Docker service

Proceed with installation?" *Waits for confirmation*
"""

# ---------------------------------------------------------------------------
# Create the Worker System Agent
# ---------------------------------------------------------------------------
worker_system_agent = Agent(
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

# ---------------------------------------------------------------------------
# Run the Agent
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Example: System health check
    worker_system_agent.print_response(
        "Check system health - show me CPU usage, memory, and disk space on /",
        stream=True
    )
