import platform
import subprocess
from typing import List, Optional

from agno.tools import Toolkit
from agno.utils.log import log_debug, log_warning


class SystemMonitorTools(Toolkit):
    def __init__(self, **kwargs):
        """Initialize SystemMonitorTools for system monitoring and diagnostics.

        Provides tools to monitor CPU, memory, disk, processes, network, and services.
        Uses psutil when available, falls back to shell commands.
        """
        tools = [
            self.get_system_info,
            self.get_cpu_usage,
            self.get_memory_info,
            self.get_disk_usage,
            self.list_processes,
            self.get_network_info,
            self.check_service_status,
        ]

        super().__init__(name="system_monitor_tools", tools=tools, **kwargs)

    def get_system_info(self) -> str:
        """Get basic system information including OS, kernel, architecture, and hostname.

        Returns:
            str: System information including OS name, version, kernel, architecture, and hostname.
        """
        try:
            info = []
            info.append(f"OS: {platform.system()} {platform.release()}")
            info.append(f"Version: {platform.version()}")
            info.append(f"Architecture: {platform.machine()}")
            info.append(f"Processor: {platform.processor()}")
            info.append(f"Hostname: {platform.node()}")
            info.append(f"Python: {platform.python_version()}")

            return "\n".join(info)
        except Exception as e:
            log_warning(f"Failed to get system info: {str(e)}")
            return f"Error: {e}"

    def get_cpu_usage(self) -> str:
        """Get CPU usage information including load average and core count.

        Returns:
            str: CPU usage information including load average, CPU count, and current usage percentage if available.
        """
        try:
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count(logical=True)
                cpu_count_physical = psutil.cpu_count(logical=False)
                load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None

                info = []
                info.append(f"CPU Usage: {cpu_percent}%")
                info.append(f"CPU Count (logical): {cpu_count}")
                info.append(f"CPU Count (physical): {cpu_count_physical}")
                if load_avg:
                    info.append(f"Load Average (1/5/15 min): {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}")

                return "\n".join(info)
            except ImportError:
                result = subprocess.run(
                    ["cat", "/proc/loadavg"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return f"Load Average: {result.stdout.strip()}"
                return "CPU info not available (install psutil for detailed stats)"
        except Exception as e:
            log_warning(f"Failed to get CPU usage: {str(e)}")
            return f"Error: {e}"

    def get_memory_info(self) -> str:
        """Get memory usage information including total, available, used, and swap.

        Returns:
            str: Memory information including RAM and swap usage with percentages.
        """
        try:
            try:
                import psutil
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()

                info = []
                info.append(f"Total RAM: {mem.total / (1024**3):.2f} GB")
                info.append(f"Available: {mem.available / (1024**3):.2f} GB")
                info.append(f"Used: {mem.used / (1024**3):.2f} GB ({mem.percent}%)")
                info.append(f"Free: {mem.free / (1024**3):.2f} GB")
                info.append(f"Swap Total: {swap.total / (1024**3):.2f} GB")
                info.append(f"Swap Used: {swap.used / (1024**3):.2f} GB ({swap.percent}%)")

                return "\n".join(info)
            except ImportError:
                result = subprocess.run(
                    ["free", "-h"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout
                return "Memory info not available (install psutil for detailed stats)"
        except Exception as e:
            log_warning(f"Failed to get memory info: {str(e)}")
            return f"Error: {e}"

    def get_disk_usage(self, path: str = "/") -> str:
        """Get disk usage information for a given path.

        Args:
            path (str): Path to check disk usage for. Defaults to root "/".

        Returns:
            str: Disk usage information including total, used, free space and percentage.
        """
        try:
            try:
                import psutil
                usage = psutil.disk_usage(path)

                info = []
                info.append(f"Path: {path}")
                info.append(f"Total: {usage.total / (1024**3):.2f} GB")
                info.append(f"Used: {usage.used / (1024**3):.2f} GB ({usage.percent}%)")
                info.append(f"Free: {usage.free / (1024**3):.2f} GB")

                return "\n".join(info)
            except ImportError:
                result = subprocess.run(
                    ["df", "-h", path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout
                return "Disk info not available (install psutil for detailed stats)"
        except Exception as e:
            log_warning(f"Failed to get disk usage: {str(e)}")
            return f"Error: {e}"

    def list_processes(self, filter: Optional[str] = None, top_n: int = 10) -> str:
        """List running processes, optionally filtered by name.

        Args:
            filter (Optional[str]): Filter processes by name (case-insensitive). If None, shows top processes by memory.
            top_n (int): Number of top processes to show. Defaults to 10.

        Returns:
            str: List of processes with PID, name, CPU%, and memory usage.
        """
        try:
            try:
                import psutil
                processes = []

                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                    try:
                        pinfo = proc.info
                        if filter:
                            if filter.lower() not in pinfo['name'].lower():
                                continue

                        mem_mb = pinfo['memory_info'].rss / (1024 * 1024) if pinfo.get('memory_info') else 0
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'cpu': pinfo.get('cpu_percent', 0),
                            'mem_percent': pinfo.get('memory_percent', 0),
                            'mem_mb': mem_mb
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if not filter:
                    processes.sort(key=lambda x: x['mem_percent'], reverse=True)
                    processes = processes[:top_n]

                if not processes:
                    return f"No processes found{' matching filter: ' + filter if filter else ''}"

                result = ["PID\tNAME\t\t\tCPU%\tMEM%\tMEM(MB)"]
                result.append("-" * 60)
                for p in processes:
                    result.append(f"{p['pid']}\t{p['name'][:20]:<20}\t{p['cpu']:.1f}\t{p['mem_percent']:.1f}\t{p['mem_mb']:.1f}")

                return "\n".join(result)
            except ImportError:
                cmd = ["ps", "aux"]
                if filter:
                    result = subprocess.run(
                        cmd + ["|", "grep", filter],
                        capture_output=True,
                        text=True,
                        shell=True
                    )
                else:
                    result = subprocess.run(
                        cmd + ["|", "head", "-n", str(top_n + 1)],
                        capture_output=True,
                        text=True,
                        shell=True
                    )

                if result.returncode == 0:
                    return result.stdout
                return "Process info not available (install psutil for detailed stats)"
        except Exception as e:
            log_warning(f"Failed to list processes: {str(e)}")
            return f"Error: {e}"

    def get_network_info(self) -> str:
        """Get network interface information including IP addresses and network statistics.

        Returns:
            str: Network interface information including addresses and connection stats.
        """
        try:
            try:
                import psutil
                info = []

                addrs = psutil.net_if_addrs()
                for interface, addr_list in addrs.items():
                    info.append(f"\nInterface: {interface}")
                    for addr in addr_list:
                        if addr.family == 2:
                            info.append(f"  IPv4: {addr.address}")
                        elif addr.family == 10:
                            info.append(f"  IPv6: {addr.address}")
                        elif addr.family == 17:
                            info.append(f"  MAC: {addr.address}")

                stats = psutil.net_io_counters()
                info.append(f"\nNetwork Stats:")
                info.append(f"  Bytes Sent: {stats.bytes_sent / (1024**2):.2f} MB")
                info.append(f"  Bytes Received: {stats.bytes_recv / (1024**2):.2f} MB")
                info.append(f"  Packets Sent: {stats.packets_sent}")
                info.append(f"  Packets Received: {stats.packets_recv}")

                return "\n".join(info)
            except ImportError:
                result = subprocess.run(
                    ["ip", "addr", "show"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout

                result = subprocess.run(
                    ["ifconfig"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    return result.stdout

                return "Network info not available (install psutil for detailed stats)"
        except Exception as e:
            log_warning(f"Failed to get network info: {str(e)}")
            return f"Error: {e}"

    def check_service_status(self, service_name: str) -> str:
        """Check the status of a systemd service.

        Args:
            service_name (str): Name of the service to check (e.g., "nginx", "docker").

        Returns:
            str: Service status information including active state and recent logs.
        """
        try:
            result = subprocess.run(
                ["systemctl", "status", service_name],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return result.stdout
            elif result.returncode == 3:
                return f"Service '{service_name}' is inactive/dead"
            elif result.returncode == 4:
                return f"Service '{service_name}' not found"
            else:
                return result.stderr if result.stderr else result.stdout
        except FileNotFoundError:
            return "systemctl not available (not a systemd system)"
        except Exception as e:
            log_warning(f"Failed to check service status: {str(e)}")
            return f"Error: {e}"
