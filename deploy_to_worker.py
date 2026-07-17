#!/usr/bin/env python3
"""Deploy Agno project to worker machine"""

import paramiko
import os
import sys
from pathlib import Path

# Worker machine config
HOST = "10.0.90.243"
USERNAME = "bianbu"
PASSWORD = "bianbu"
REMOTE_PATH = "/home/bianbu/agno-riscv64"

def run_command(ssh_client, command, show_output=True):
    """Execute command on remote machine"""
    print(f"Running: {command}")
    stdin, stdout, stderr = ssh_client.exec_command(command)
    exit_code = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if show_output:
        if output:
            print(output)
        if error:
            print(f"Error: {error}", file=sys.stderr)

    return exit_code, output, error

def main():
    print(f"Connecting to {USERNAME}@{HOST}...")

    # Create SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(HOST, username=USERNAME, password=PASSWORD)
        print("Connected successfully!")

        # Check system info
        print("\n=== System Information ===")
        run_command(ssh, "uname -a")
        run_command(ssh, "python3 --version")
        run_command(ssh, "git --version")

        # Check if target directory exists
        print(f"\n=== Checking remote path: {REMOTE_PATH} ===")
        exit_code, output, _ = run_command(ssh, f"ls -la {REMOTE_PATH}", show_output=False)

        if exit_code != 0:
            print(f"Directory {REMOTE_PATH} does not exist. Creating...")
            run_command(ssh, f"mkdir -p {REMOTE_PATH}")
        else:
            print(f"Directory {REMOTE_PATH} exists")
            run_command(ssh, f"ls -la {REMOTE_PATH}")

        # Check if git repo exists
        print("\n=== Checking for existing repository ===")
        exit_code, _, _ = run_command(ssh, f"test -d {REMOTE_PATH}/.git", show_output=False)

        if exit_code == 0:
            print("Git repository exists, pulling latest changes...")
            run_command(ssh, f"cd {REMOTE_PATH} && git fetch && git status")
        else:
            print("No git repository found. Need to clone or sync files.")
            print("\nOptions:")
            print("1. Clone from git (if you have git URL)")
            print("2. Use rsync to sync local files")

        # Check Python environment
        print("\n=== Checking Python environment ===")
        run_command(ssh, f"cd {REMOTE_PATH} && python3 -m venv --help | head -5")

        print("\n=== Deployment preparation complete ===")
        print(f"Remote path: {REMOTE_PATH}")
        print("Next steps:")
        print("1. Sync project files to worker machine")
        print("2. Run ./scripts/dev_setup.sh to setup development environment")
        print("3. Run ./scripts/demo_setup.sh to setup demo environment")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    finally:
        ssh.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
