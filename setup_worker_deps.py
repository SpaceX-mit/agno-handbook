#!/usr/bin/env python3
"""Install dependencies and test system agent on worker machine."""

import paramiko
import sys

HOST = "10.0.90.243"
USERNAME = "bianbu"
PASSWORD = "bianbu"
REMOTE_PATH = "/home/bianbu/agno-riscv64"


def run_command(ssh, command, show_output=True, timeout=300):
    """Execute command on remote machine."""
    print(f"\n> {command}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if show_output:
        if output:
            print(output)
        if error and exit_code != 0:
            print(f"ERROR: {error}", file=sys.stderr)

    return exit_code, output, error


def main():
    print("=== Setting up dependencies on worker machine ===\n")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✓ Connected\n")

        # Install agno package in development mode
        print("Installing Agno in development mode...")
        run_command(ssh,
            f"cd {REMOTE_PATH} && .venv/bin/pip install -e libs/agno",
            timeout=600)

        # Test imports
        print("\nTesting imports...")
        test_code = """
import sys
sys.path.insert(0, 'libs/agno')
from agno.tools.system_monitor import SystemMonitorTools
from agno.tools.package_manager import PackageManagerTools

print('Imports successful')

# Test system monitor
tools = SystemMonitorTools()
print('\\n--- System Info ---')
print(tools.get_system_info())
print('\\n--- CPU Usage ---')
print(tools.get_cpu_usage())
print('\\n--- Memory Info ---')
print(tools.get_memory_info())
print('\\n--- Disk Usage ---')
print(tools.get_disk_usage('/'))
"""
        exit_code, output, error = run_command(ssh,
            f"cd {REMOTE_PATH} && .venv/bin/python -c '{test_code}'")

        if exit_code == 0:
            print("\n✓ System agent tools working correctly!")
        else:
            print("\n✗ Tests failed")
            return 1

        print("\n" + "=" * 70)
        print("Setup Complete!")
        print("=" * 70)
        print("\nTo use the system agent:")
        print(f"  ssh {USERNAME}@{HOST}")
        print(f"  cd {REMOTE_PATH}")
        print(f"  source .venv/bin/activate")
        print(f"  export OPENAI_API_KEY='your-key'")
        print(f"  python cookbook/system_agent/cli.py")
        print("\nOr test without API key:")
        print(f"  python -c 'from cookbook.system_agent.worker_system_agent import *'")
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()


if __name__ == "__main__":
    sys.exit(main())
