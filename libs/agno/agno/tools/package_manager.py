import subprocess
from typing import List, Optional

from agno.tools import Toolkit
from agno.utils.log import log_debug, log_warning


class PackageManagerTools(Toolkit):
    def __init__(self, **kwargs):
        """Initialize PackageManagerTools for package management operations.

        Provides tools to search, install, remove, and update packages using apt/dpkg.
        Destructive operations (install, remove, upgrade) should be gated with
        requires_confirmation_tools for safety.
        """
        tools = [
            self.search_package,
            self.install_package,
            self.remove_package,
            self.update_package_list,
            self.upgrade_packages,
            self.list_installed_packages,
            self.get_package_info,
        ]

        super().__init__(name="package_manager_tools", tools=tools, **kwargs)

    def search_package(self, name: str) -> str:
        """Search for packages by name using apt-cache.

        Args:
            name (str): Package name or pattern to search for.

        Returns:
            str: List of matching packages with descriptions.
        """
        try:
            log_debug(f"Searching for package: {name}")
            result = subprocess.run(
                ["apt-cache", "search", name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                if not result.stdout.strip():
                    return f"No packages found matching '{name}'"
                return result.stdout
            else:
                return f"Error searching packages: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Search timed out after 30 seconds"
        except FileNotFoundError:
            return "Error: apt-cache not found (not a Debian/Ubuntu system)"
        except Exception as e:
            log_warning(f"Failed to search package: {str(e)}")
            return f"Error: {e}"

    def install_package(self, name: str, assume_yes: bool = False) -> str:
        """Install a package using apt-get.

        .. warning::
            This operation modifies the system. Gate this tool with
            ``requires_confirmation_tools=["install_package"]`` to require
            human approval before installation.

        Args:
            name (str): Package name to install.
            assume_yes (bool): If True, automatically answer yes to prompts (use with caution).

        Returns:
            str: Installation result or error message.
        """
        try:
            log_debug(f"Installing package: {name}")
            cmd = ["apt-get", "install"]
            if assume_yes:
                cmd.append("-y")
            cmd.append(name)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return f"Successfully installed {name}\n\n{result.stdout}"
            else:
                return f"Error installing {name}: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Installation timed out after 5 minutes"
        except PermissionError:
            return "Error: Permission denied. Need sudo privileges to install packages"
        except FileNotFoundError:
            return "Error: apt-get not found (not a Debian/Ubuntu system)"
        except Exception as e:
            log_warning(f"Failed to install package: {str(e)}")
            return f"Error: {e}"

    def remove_package(self, name: str, assume_yes: bool = False) -> str:
        """Remove a package using apt-get.

        .. warning::
            This operation modifies the system. Gate this tool with
            ``requires_confirmation_tools=["remove_package"]`` to require
            human approval before removal.

        Args:
            name (str): Package name to remove.
            assume_yes (bool): If True, automatically answer yes to prompts (use with caution).

        Returns:
            str: Removal result or error message.
        """
        try:
            log_debug(f"Removing package: {name}")
            cmd = ["apt-get", "remove"]
            if assume_yes:
                cmd.append("-y")
            cmd.append(name)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                return f"Successfully removed {name}\n\n{result.stdout}"
            else:
                return f"Error removing {name}: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Removal timed out after 5 minutes"
        except PermissionError:
            return "Error: Permission denied. Need sudo privileges to remove packages"
        except FileNotFoundError:
            return "Error: apt-get not found (not a Debian/Ubuntu system)"
        except Exception as e:
            log_warning(f"Failed to remove package: {str(e)}")
            return f"Error: {e}"

    def update_package_list(self) -> str:
        """Update the package list using apt-get update.

        Returns:
            str: Update result or error message.
        """
        try:
            log_debug("Updating package list")
            result = subprocess.run(
                ["apt-get", "update"],
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.returncode == 0:
                return f"Package list updated successfully\n\n{result.stdout}"
            else:
                return f"Error updating package list: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Update timed out after 2 minutes"
        except PermissionError:
            return "Error: Permission denied. Need sudo privileges to update package list"
        except FileNotFoundError:
            return "Error: apt-get not found (not a Debian/Ubuntu system)"
        except Exception as e:
            log_warning(f"Failed to update package list: {str(e)}")
            return f"Error: {e}"

    def upgrade_packages(self, assume_yes: bool = False) -> str:
        """Upgrade all packages using apt-get upgrade.

        .. warning::
            This operation modifies the system. Gate this tool with
            ``requires_confirmation_tools=["upgrade_packages"]`` to require
            human approval before upgrading.

        Args:
            assume_yes (bool): If True, automatically answer yes to prompts (use with caution).

        Returns:
            str: Upgrade result or error message.
        """
        try:
            log_debug("Upgrading packages")
            cmd = ["apt-get", "upgrade"]
            if assume_yes:
                cmd.append("-y")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                return f"Packages upgraded successfully\n\n{result.stdout}"
            else:
                return f"Error upgrading packages: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Upgrade timed out after 10 minutes"
        except PermissionError:
            return "Error: Permission denied. Need sudo privileges to upgrade packages"
        except FileNotFoundError:
            return "Error: apt-get not found (not a Debian/Ubuntu system)"
        except Exception as e:
            log_warning(f"Failed to upgrade packages: {str(e)}")
            return f"Error: {e}"

    def list_installed_packages(self, filter: Optional[str] = None) -> str:
        """List installed packages using dpkg.

        Args:
            filter (Optional[str]): Filter packages by name pattern. If None, lists all packages.

        Returns:
            str: List of installed packages with versions.
        """
        try:
            log_debug(f"Listing installed packages{' matching: ' + filter if filter else ''}")
            cmd = ["dpkg", "-l"]
            if filter:
                cmd.append(filter)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) <= 5:
                    return f"No packages found{' matching: ' + filter if filter else ''}"
                return result.stdout
            else:
                return f"Error listing packages: {result.stderr}"
        except subprocess.TimeoutExpired:
            return "Error: Listing timed out after 30 seconds"
        except FileNotFoundError:
            return "Error: dpkg not found (not a Debian/Ubuntu system)"
        except Exception as e:
            log_warning(f"Failed to list packages: {str(e)}")
            return f"Error: {e}"

    def get_package_info(self, name: str) -> str:
        """Get detailed information about a package.

        Args:
            name (str): Package name to get information about.

        Returns:
            str: Detailed package information including version, description, dependencies, etc.
        """
        try:
            log_debug(f"Getting info for package: {name}")
            result = subprocess.run(
                ["apt-cache", "show", name],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return result.stdout
            else:
                return f"Error getting package info: {result.stderr or 'Package not found'}"
        except subprocess.TimeoutExpired:
            return "Error: Query timed out after 30 seconds"
        except FileNotFoundError:
            return "Error: apt-cache not found (not a Debian/Ubuntu system)"
        except Exception as e:
            log_warning(f"Failed to get package info: {str(e)}")
            return f"Error: {e}"
