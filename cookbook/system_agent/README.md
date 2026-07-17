# Worker System Agent

An AI-powered system administrator assistant that can monitor, manage, and operate Linux systems through natural language commands.

## Overview

The Worker System Agent combines multiple toolkits to provide comprehensive system management capabilities:

- **System Monitoring**: CPU, memory, disk, processes, network, services
- **File Operations**: Read, write, search, manage files and directories
- **Shell Execution**: Run system commands with safety confirmations
- **Package Management**: Search, install, remove, update packages (apt/dpkg)

## Quick Start

### Prerequisites

1. Python 3.10+ installed
2. OpenAI API key (or use Gemini with Google API key)
3. psutil package (optional, for enhanced system monitoring)

### Installation

```bash
# Navigate to the agno-riscv64 directory
cd /home/bianbu/agno-riscv64

# Activate virtual environment
source .venv/bin/activate

# Install optional dependencies
pip install psutil

# Set API key
export OPENAI_API_KEY='your-key-here'
```

### Run the Agent

**Interactive CLI (recommended)**:
```bash
python cookbook/system_agent/cli.py
```

**Single command**:
```bash
python cookbook/system_agent/worker_system_agent.py
```

**Custom script**:
```python
from cookbook.system_agent.worker_system_agent import worker_system_agent

response = worker_system_agent.run("Check system health")
print(response.content)
```

## Example Commands

### System Monitoring

```
Check system health - show CPU, memory, and disk usage
```

```
List the top 10 processes by memory usage
```

```
Show me network interface information
```

```
Is the docker service running?
```

### File Operations

```
List all Python files in the current directory
```

```
Search for files containing 'agent' in their name
```

```
Read the README.md file
```

```
Create a backup directory called backup-2026
```

### Shell Commands

```
Show the current git branch
```

```
Count how many Python files are in the libs directory
```

```
Check the Python version installed
```

### Package Management

```
Is psutil installed? Show me the version
```

```
Search for packages related to docker
```

```
Install the htop package (requires confirmation)
```

```
List all installed Python packages
```

## Safety Features

### Confirmation Required

The agent will ask for confirmation before:
- Running any shell command
- Installing or removing packages
- Upgrading system packages
- Deleting files

### Example Confirmation Flow

```
You: Install htop

Agent: I'll install htop using apt. This requires sudo privileges.

----------------------------------------------------------------------
CONFIRMATION REQUIRED
----------------------------------------------------------------------

Tool: install_package
Args: {'name': 'htop'}

Approve this action? [y/N]: y
✓ Approved
----------------------------------------------------------------------

Agent: Successfully installed htop...
```

### Path Restrictions

File operations are restricted to:
- Base directory: `/home/bianbu/agno-riscv64`
- Cannot access parent directories without explicit permission

## Architecture

### Components

```
Worker System Agent
├── SystemMonitorTools     # CPU, memory, disk, processes, network
├── ShellTools            # Execute shell commands
├── FileTools             # File and directory operations
└── PackageManagerTools   # apt/dpkg package management
```

### Tool Details

**SystemMonitorTools** (`libs/agno/agno/tools/system_monitor.py`):
- `get_system_info()` - OS, kernel, architecture
- `get_cpu_usage()` - CPU utilization and load
- `get_memory_info()` - RAM and swap usage
- `get_disk_usage(path)` - Disk space
- `list_processes(filter, top_n)` - Running processes
- `get_network_info()` - Network interfaces
- `check_service_status(name)` - Systemd service status

**PackageManagerTools** (`libs/agno/agno/tools/package_manager.py`):
- `search_package(name)` - Search apt packages
- `install_package(name)` - Install package (requires confirmation)
- `remove_package(name)` - Remove package (requires confirmation)
- `update_package_list()` - apt update
- `upgrade_packages()` - apt upgrade (requires confirmation)
- `list_installed_packages(filter)` - List installed packages
- `get_package_info(name)` - Package details

## Configuration

### Using Different Models

**Gemini (default in original example)**:
```python
from agno.models.google import Gemini

agent = Agent(
    model=Gemini(id="gemini-3.5-flash"),
    ...
)
```

**OpenAI GPT-5.5**:
```python
from agno.models.openai import OpenAIResponses

agent = Agent(
    model=OpenAIResponses(id="gpt-5.5"),
    ...
)
```

### Customizing Base Directory

Change the working directory for file and shell operations:

```python
ShellTools(base_dir="/your/custom/path")
FileTools(base_dir=Path("/your/custom/path"))
```

### Disabling Confirmations (NOT RECOMMENDED)

For automation only, remove confirmation requirements:

```python
# WARNING: This allows unrestricted command execution
ShellTools(requires_confirmation_tools=[])
PackageManagerTools(requires_confirmation_tools=[])
```

## Troubleshooting

### API Key Not Set

```
Error: OPENAI_API_KEY not set in environment
```

**Solution**:
```bash
export OPENAI_API_KEY='your-key-here'
```

### psutil Not Installed

System monitoring will fall back to basic shell commands. For enhanced features:

```bash
pip install psutil
```

### Permission Denied

Package management operations require sudo:

```bash
# Run as root or with sudo access
sudo python cookbook/system_agent/cli.py
```

Or pre-configure passwordless sudo for specific commands.

### Connection Issues

If the agent cannot reach the API:
- Check internet connectivity
- Verify API key is valid
- Check firewall settings

## Development

### Adding New Tools

1. Create tool class in `libs/agno/agno/tools/`
2. Import in `worker_system_agent.py`
3. Add to agent's tools list
4. Update documentation

### Testing

See `TEST_LOG.md` for test results and procedures.

## Security Considerations

1. **Never disable confirmations** in production
2. **Limit file access** to specific directories
3. **Review logs** for suspicious activity
4. **Use API key management** (environment variables, not hardcoded)
5. **Run with minimal privileges** when possible
6. **Audit tool usage** regularly

## License

Same as Agno framework.

## Support

For issues or questions:
- Check `TEST_LOG.md` for known issues
- Review Agno documentation
- Open issue in repository
