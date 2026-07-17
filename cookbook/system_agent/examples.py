"""
Worker System Agent - Usage Examples
=====================================

Demonstrates various use cases for the system agent.
"""

from cookbook.system_agent.worker_system_agent import worker_system_agent


def example_1_system_health_check():
    """Example 1: Complete system health check."""
    print("\n" + "=" * 70)
    print("Example 1: System Health Check")
    print("=" * 70 + "\n")

    worker_system_agent.print_response(
        "Perform a complete system health check. Show me:\n"
        "1. CPU usage and load average\n"
        "2. Memory usage (RAM and swap)\n"
        "3. Disk usage for / partition\n"
        "4. Top 5 processes by memory usage",
        stream=True
    )


def example_2_file_management():
    """Example 2: File operations and management."""
    print("\n" + "=" * 70)
    print("Example 2: File Management")
    print("=" * 70 + "\n")

    worker_system_agent.print_response(
        "List all Python files in the libs/agno/agno/tools directory. "
        "Show me the file names and their sizes.",
        stream=True
    )


def example_3_process_monitoring():
    """Example 3: Monitor specific processes."""
    print("\n" + "=" * 70)
    print("Example 3: Process Monitoring")
    print("=" * 70 + "\n")

    worker_system_agent.print_response(
        "Find all Python processes currently running. "
        "Show me the process ID, name, and memory usage.",
        stream=True
    )


def example_4_package_check():
    """Example 4: Check installed packages."""
    print("\n" + "=" * 70)
    print("Example 4: Package Information")
    print("=" * 70 + "\n")

    worker_system_agent.print_response(
        "Check if psutil and docker are installed. "
        "For each, show whether it's installed and the version if available.",
        stream=True
    )


def example_5_network_diagnostics():
    """Example 5: Network information."""
    print("\n" + "=" * 70)
    print("Example 5: Network Diagnostics")
    print("=" * 70 + "\n")

    worker_system_agent.print_response(
        "Show me network interface information. "
        "Include IP addresses and basic network statistics.",
        stream=True
    )


def example_6_service_status():
    """Example 6: Check service status."""
    print("\n" + "=" * 70)
    print("Example 6: Service Status Check")
    print("=" * 70 + "\n")

    worker_system_agent.print_response(
        "Check if the ssh service is running. "
        "Show me its current status.",
        stream=True
    )


def example_7_combined_task():
    """Example 7: Complex multi-step task."""
    print("\n" + "=" * 70)
    print("Example 7: Combined Task")
    print("=" * 70 + "\n")

    worker_system_agent.print_response(
        "I need to prepare for a deployment. Please:\n"
        "1. Check if we have at least 5GB free disk space\n"
        "2. Check if Python 3.10+ is installed\n"
        "3. List all files in the cookbook/system_agent directory\n"
        "4. Verify memory usage is below 80%",
        stream=True
    )


def example_8_search_files():
    """Example 8: Search and analyze files."""
    print("\n" + "=" * 70)
    print("Example 8: File Search")
    print("=" * 70 + "\n")

    worker_system_agent.print_response(
        "Search for all files containing 'agent' in their name "
        "within the libs/agno/agno directory. "
        "Show me the count and list the first 10 matches.",
        stream=True
    )


# ---------------------------------------------------------------------------
# Main - Run all examples
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    examples = {
        "1": ("System Health Check", example_1_system_health_check),
        "2": ("File Management", example_2_file_management),
        "3": ("Process Monitoring", example_3_process_monitoring),
        "4": ("Package Information", example_4_package_check),
        "5": ("Network Diagnostics", example_5_network_diagnostics),
        "6": ("Service Status", example_6_service_status),
        "7": ("Combined Task", example_7_combined_task),
        "8": ("File Search", example_8_search_files),
    }

    if len(sys.argv) > 1:
        # Run specific example
        example_num = sys.argv[1]
        if example_num in examples:
            name, func = examples[example_num]
            print(f"\nRunning Example {example_num}: {name}\n")
            func()
        else:
            print(f"Example {example_num} not found.")
            print("\nAvailable examples:")
            for num, (name, _) in examples.items():
                print(f"  {num}: {name}")
    else:
        # Run all examples
        print("\nRunning all examples...")
        print("Note: This will make multiple API calls.\n")

        for num, (name, func) in examples.items():
            try:
                func()
                print("\n✓ Example completed\n")
            except Exception as e:
                print(f"\n✗ Example failed: {e}\n")

        print("\n" + "=" * 70)
        print("All examples completed")
        print("=" * 70)
