#!/usr/bin/env python3
"""Deploy system agent to worker machine and run tests."""

import paramiko
import sys

HOST = "10.0.90.243"
USERNAME = "bianbu"
PASSWORD = "bianbu"
REMOTE_PATH = "/home/bianbu/agno-riscv64"


def run_command(ssh, command, show_output=True):
    """Execute command on remote machine."""
    print(f"\n> {command}")
    stdin, stdout, stderr = ssh.exec_command(command, timeout=60)
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
    print("=== Deploying System Agent to Worker Machine ===\n")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✓ Connected to worker machine\n")

        # Step 1: Update repository
        print("Step 1: Pulling latest code...")
        run_command(ssh, f"cd {REMOTE_PATH} && git pull")

        # Step 2: Install psutil
        print("\nStep 2: Installing psutil...")
        run_command(ssh, f"cd {REMOTE_PATH} && .venv/bin/pip install psutil")

        # Step 3: Test system monitor tools
        print("\nStep 3: Testing SystemMonitorTools...")
        test_code = """
import sys
sys.path.insert(0, 'libs/agno')
from agno.tools.system_monitor import SystemMonitorTools

tools = SystemMonitorTools()
print('System Info:')
print(tools.get_system_info())
print('\\nCPU Usage:')
print(tools.get_cpu_usage())
print('\\nMemory Info:')
print(tools.get_memory_info())
"""
        exit_code, output, error = run_command(ssh,
            f"cd {REMOTE_PATH} && .venv/bin/python -c \"{test_code}\"")

        if exit_code == 0:
            print("✓ SystemMonitorTools working")
        else:
            print("✗ SystemMonitorTools test failed")

        # Step 4: Test package manager tools
        print("\nStep 4: Testing PackageManagerTools...")
        test_code2 = """
import sys
sys.path.insert(0, 'libs/agno')
from agno.tools.package_manager import PackageManagerTools

tools = PackageManagerTools()
print('Searching for python3:')
print(tools.search_package('python3'))
"""
        exit_code, output, error = run_command(ssh,
            f"cd {REMOTE_PATH} && .venv/bin/python -c \"{test_code2}\"")

        if exit_code == 0:
            print("✓ PackageManagerTools working")
        else:
            print("✗ PackageManagerTools test failed")

        # Step 5: Check if examples exist
        print("\nStep 5: Verifying cookbook files...")
        exit_code, output, error = run_command(ssh,
            f"ls -la {REMOTE_PATH}/cookbook/system_agent/")

        if exit_code == 0:
            print("✓ Cookbook files deployed")
        else:
            print("✗ Cookbook files not found")

        print("\n" + "=" * 70)
        print("Deployment Summary")
        print("=" * 70)
        print(f"Remote path: {REMOTE_PATH}/cookbook/system_agent/")
        print("\nTo use the system agent:")
        print(f"  ssh {USERNAME}@{HOST}")
        print(f"  cd {REMOTE_PATH}")
        print(f"  export OPENAI_API_KEY='your-key'")
        print(f"  python cookbook/system_agent/cli.py")
        print("\nOr run examples:")
        print(f"  python cookbook/system_agent/examples.py 1")
        print("=" * 70)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
