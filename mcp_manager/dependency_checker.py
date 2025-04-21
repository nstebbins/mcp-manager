"""Module for checking if required dependencies are installed."""

import shutil
import subprocess
from typing import List, Tuple


def check_nodejs_npm() -> Tuple[bool, List[str]]:
    """
    Check if Node.js and npm are installed.

    Returns:
        Tuple of (all_installed: bool, missing_deps: List[str])
    """
    missing = []

    # Check node
    if not shutil.which("node"):
        missing.append("Node.js")

    # Check npm
    if not shutil.which("npm"):
        missing.append("npm")

    return len(missing) == 0, missing


def check_docker() -> Tuple[bool, List[str]]:
    """
    Check if Docker is installed and running.

    Returns:
        Tuple of (all_installed: bool, missing_deps: List[str])
    """
    missing = []

    # Check if docker is installed
    if not shutil.which("docker"):
        missing.append("Docker")
        return False, missing

    # Check if docker daemon is running
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        missing.append("Docker daemon (not running)")

    return len(missing) == 0, missing


def check_dependencies(dependencies: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if all required dependencies are installed.

    Args:
        dependencies: List of dependency names to check

    Returns:
        Tuple of (all_installed: bool, missing_deps: List[str])
    """
    missing = []

    for dep in dependencies:
        if dep in ["Node.js", "npm"]:
            installed, missing_deps = check_nodejs_npm()
            if not installed:
                missing.extend(missing_deps)
        elif dep == "Docker":
            installed, missing_deps = check_docker()
            if not installed:
                missing.extend(missing_deps)

    return len(missing) == 0, missing
