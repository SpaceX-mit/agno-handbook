#!/usr/bin/env python3
"""Simple test of system agent on worker machine."""

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
        if error:
            print(f"STDERR: {error}")

    return exit_code, output, error


def main():
    print("=== Testing System Agent on Worker Machine ===\n")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("Connected to worker machine\n")

        # Test 1: Create a simple test script
        print("Creating test script...")
        test_script = """#!/usr/bin/env python3
import sys
sys.path.insert(0, 'libs/agno')

print('Testing SystemMonitorTools...')
from agno.tools.system_monitor import SystemMonitorTools
tools = SystemMonitorTools()

print('System Info:')
print(tools.get_system_info())

print('\\nCPU Usage:')
print(tools.get_cpu_usage())

print('\\nMemory Info:')
print(tools.get_memory_info())

print('\\nDisk Usage:')
print(tools.get_disk_usage('/'))

print('\\nTop 5 Processes:')
print(tools.list_processes(top_n=5))

print('\\nAll tests passed!')
"""

        run_command(ssh, f"cat > {REMOTE_PATH}/test_system_agent.py << 'ENDOFFILE'\n{test_script}\nENDOFFILE")

        # Test 2: Run the test script
        print("\nRunning test script...")
        exit_code, output, error = run_command(ssh,
            f"cd {REMOTE_PATH} && .venv/bin/python test_system_agent.py")

        if exit_code == 0:
            print("\n" + "=" * 70)
            print("SUCCESS: System Agent is working on worker machine!")
            print("=" * 70)
        else:
            print("\n" + "=" * 70)
            print("FAILED: Tests did not complete successfully")
            print("=" * 70)
            return 1

        # Show usage instructions
        print("\nTo use the system agent interactively:")
        print(f"  ssh {USERNAME}@{HOST}")
        print(f"  cd {REMOTE_PATH}")
        print(f"  export OPENAI_API_KEY='your-key-here'")
        print(f"  .venv/bin/python cookbook/system_agent/cli.py")

        print("\nOr run examples:")
        print(f"  .venv/bin/python cookbook/system_agent/examples.py 1")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    finally:
        ssh.close()


if __name__ == "__main__":
    sys.exit(main())
