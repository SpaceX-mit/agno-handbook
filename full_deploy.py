#!/usr/bin/env python3
"""Complete deployment script for Agno project on worker machine"""

import paramiko
import sys
import time

# Worker machine config
HOST = "10.0.90.243"
USERNAME = "bianbu"
PASSWORD = "bianbu"
REMOTE_PATH = "/home/bianbu/agno-riscv64"
GIT_REPO = "git@github.com:SpaceX-mit/agno-handbook.git"

def run_command(ssh_client, command, show_output=True, timeout=300):
    """Execute command on remote machine"""
    print(f"\n> {command}")
    stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
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
    print(f"=== Deploying Agno to {HOST} ===\n")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"Connecting to {USERNAME}@{HOST}...")
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✓ Connected\n")

        # Step 1: Check if directory exists and clean if needed
        print("=== Step 1: Prepare directory ===")
        exit_code, _, _ = run_command(ssh, f"test -d {REMOTE_PATH}/.git", show_output=False)

        if exit_code == 0:
            print(f"Git repository already exists at {REMOTE_PATH}")
            print("Updating existing repository...")
            run_command(ssh, f"cd {REMOTE_PATH} && git fetch origin && git reset --hard origin/main")
        else:
            # Try to clone the repository
            print(f"Cloning repository to {REMOTE_PATH}...")
            exit_code, output, error = run_command(ssh,
                f"git clone {GIT_REPO} {REMOTE_PATH}",
                show_output=True,
                timeout=600)

            if exit_code != 0:
                print("\n⚠ Git clone failed. This might be because:")
                print("1. SSH keys are not set up on worker machine")
                print("2. Worker machine cannot access GitHub")
                print("\nTrying HTTPS URL instead...")
                https_url = GIT_REPO.replace("git@github.com:", "https://github.com/")
                exit_code, _, _ = run_command(ssh,
                    f"git clone {https_url} {REMOTE_PATH}",
                    timeout=600)

                if exit_code != 0:
                    print("\n✗ Failed to clone repository")
                    print("You may need to manually copy files or setup SSH keys on worker machine")
                    return 1

        print("✓ Repository ready\n")

        # Step 2: Check Python and dependencies
        print("=== Step 2: Check Python environment ===")
        run_command(ssh, f"cd {REMOTE_PATH} && python3 --version")
        run_command(ssh, f"cd {REMOTE_PATH} && which pip3")

        # Step 3: Setup virtual environment for development
        print("\n=== Step 3: Setup development environment ===")
        print("Checking if .venv exists...")
        exit_code, _, _ = run_command(ssh, f"test -d {REMOTE_PATH}/.venv", show_output=False)

        if exit_code != 0:
            print("Creating .venv...")
            run_command(ssh, f"cd {REMOTE_PATH} && python3 -m venv .venv", timeout=120)
        else:
            print(".venv already exists")

        # Check if dev_setup.sh exists
        print("\nChecking for setup scripts...")
        exit_code, _, _ = run_command(ssh, f"test -f {REMOTE_PATH}/scripts/dev_setup.sh", show_output=False)

        if exit_code == 0:
            print("Running dev_setup.sh...")
            exit_code, output, error = run_command(ssh,
                f"cd {REMOTE_PATH} && bash ./scripts/dev_setup.sh",
                timeout=600)

            if exit_code == 0:
                print("✓ Development environment setup complete")
            else:
                print("⚠ dev_setup.sh had issues, but continuing...")
        else:
            print("dev_setup.sh not found, skipping")

        # Step 4: Setup demo environment
        print("\n=== Step 4: Setup demo environment ===")
        exit_code, _, _ = run_command(ssh, f"test -f {REMOTE_PATH}/scripts/demo_setup.sh", show_output=False)

        if exit_code == 0:
            print("Running demo_setup.sh...")
            exit_code, output, error = run_command(ssh,
                f"cd {REMOTE_PATH} && bash ./scripts/demo_setup.sh",
                timeout=600)

            if exit_code == 0:
                print("✓ Demo environment setup complete")
            else:
                print("⚠ demo_setup.sh had issues")
        else:
            print("demo_setup.sh not found, skipping")

        # Step 5: Verify installation
        print("\n=== Step 5: Verify installation ===")
        run_command(ssh, f"cd {REMOTE_PATH} && ls -la")
        run_command(ssh, f"cd {REMOTE_PATH} && test -d .venv && echo '.venv exists' || echo '.venv missing'")
        run_command(ssh, f"cd {REMOTE_PATH} && test -d .venvs/demo && echo '.venvs/demo exists' || echo '.venvs/demo missing'")

        # Check if we can import agno
        print("\nTesting agno import...")
        exit_code, output, error = run_command(ssh,
            f"cd {REMOTE_PATH} && .venv/bin/python -c 'import sys; sys.path.insert(0, \"libs/agno\"); import agno; print(f\"Agno imported successfully from {{agno.__file__}}\")'",
            show_output=True)

        if exit_code == 0:
            print("✓ Agno can be imported")
        else:
            print("⚠ Agno import test failed")

        print("\n" + "="*60)
        print("=== Deployment Summary ===")
        print(f"Remote path: {REMOTE_PATH}")
        print(f"Host: {HOST}")
        print("\nTo access the worker machine:")
        print(f"  ssh {USERNAME}@{HOST}")
        print(f"  Password: {PASSWORD}")
        print("\nTo run cookbooks:")
        print(f"  cd {REMOTE_PATH}")
        print(f"  .venvs/demo/bin/python cookbook/<folder>/<file>.py")
        print("\nTo run tests:")
        print(f"  cd {REMOTE_PATH}")
        print(f"  source .venv/bin/activate")
        print(f"  pytest libs/agno/tests/")
        print("="*60)

    except paramiko.ssh_exception.NoValidConnectionsError as e:
        print(f"✗ Connection failed: {e}", file=sys.stderr)
        print("Check if the worker machine is accessible from your network")
        return 1
    except paramiko.ssh_exception.AuthenticationException as e:
        print(f"✗ Authentication failed: {e}", file=sys.stderr)
        return 1
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
