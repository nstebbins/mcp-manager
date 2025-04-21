import copy
import json
import os
from enum import Enum
from pathlib import Path
from typing import Optional

import typer

from .dependency_checker import check_dependencies
from .server_registry import get_claude_config, get_server_info, search_servers

app = typer.Typer()


class ClientType(str, Enum):
    CURSOR = "cursor"
    CLAUDE = "claude"


class ScopeType(str, Enum):
    GLOBAL = "global"
    PROJECT = "project"


# Define options at module level
client_option = typer.Option(None, help="Client type (cursor or claude)")
scope_option = typer.Option(None, help="Installation scope (global or project)")


@app.command()
def search(keyword: str):
    """
    Search the online registry for servers matching the keyword.
    """
    matches = search_servers(keyword)
    if not matches:
        typer.echo(f"No servers found matching: {keyword}")
        return

    typer.echo(f"Found {len(matches)} matching servers:")
    for server_name in matches:
        info = get_server_info(server_name)
        typer.echo(f"\n{server_name}:")
        typer.echo(f"  Description: {info['description']}")
        typer.echo(f"  Maintainer: {info['maintainer']}")


@app.command()
def info(server_name: str):
    """
    Display detailed information about a specific server.
    """
    server_info = get_server_info(server_name)
    if not server_info:
        typer.echo(f"Server not found: {server_name}")
        return

    typer.echo(f"\nServer: {server_name}")
    typer.echo(f"Description: {server_info['description']}")
    typer.echo(f"Maintainer: {server_info['maintainer']}")

    if server_info["required_config"]:
        typer.echo("\nRequired configuration:")
        for config in server_info["required_config"]:
            typer.echo(f"- {config}")

    if server_info["dependencies"]:
        typer.echo("\nDependencies:")
        for dep in server_info["dependencies"]:
            typer.echo(f"- {dep}")


@app.command()
def install(
    server_name: str,
    client: Optional[ClientType] = client_option,
    scope: Optional[ScopeType] = scope_option,
):
    """
    Install a server with optional client type and scope specifications.
    """
    # Get server info and config
    server_info = get_server_info(server_name)
    if not server_info:
        typer.echo(f"Server not found: {server_name}")
        return

    # For now, we only support Claude installation
    if client and client != ClientType.CLAUDE:
        typer.echo("Currently only Claude installation is supported")
        return

    # Check dependencies before proceeding
    dependencies = server_info.dependencies
    if dependencies:
        all_installed, missing_deps = check_dependencies(dependencies)
        if not all_installed:
            typer.echo("Missing required dependencies:")
            for dep in missing_deps:
                typer.echo(f"- {dep}")
            typer.echo("\nPlease install the missing dependencies and try again.")
            return

    # Get Claude config
    claude_config = get_claude_config(server_name)
    if not claude_config:
        typer.echo(f"No Claude configuration available for server: {server_name}")
        return

    # Handle user input if required
    if server_info.requires_user_input:
        if server_info.user_input_prompt:
            user_input = typer.prompt(server_info.user_input_prompt)
            # Make a deep copy to avoid modifying the original config
            claude_config = copy.deepcopy(claude_config)
            # Replace placeholder in args with user input
            claude_config["args"] = [
                arg.replace("{user_directory}", user_input) if isinstance(arg, str) else arg
                for arg in claude_config["args"]
            ]

    # Get Claude config file path
    config_dir = Path(os.path.expanduser("~/Library/Application Support/Claude"))
    config_file = config_dir / "claude_desktop_config.json"

    if not config_file.exists():
        typer.echo(f"Claude config file not found at: {config_file}")
        return

    try:
        # Read current config
        with open(config_file) as f:
            config = json.load(f)

        # Initialize mcpServers if it doesn't exist
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Add or update server config
        config["mcpServers"][server_name] = claude_config

        # Write updated config
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        typer.echo(f"Successfully installed {server_name} for Claude")

    except Exception as e:
        typer.echo(f"Error updating Claude config: {str(e)}")
        return


@app.command()
def uninstall(
    server_name: str,
    client: Optional[ClientType] = client_option,
):
    """
    Remove a server from the client configuration.
    """
    # For now, we only support Claude deletion
    if client and client != ClientType.CLAUDE:
        typer.echo("Currently only Claude deletion is supported")
        return

    # Get Claude config file path
    config_dir = Path(os.path.expanduser("~/Library/Application Support/Claude"))
    config_file = config_dir / "claude_desktop_config.json"

    if not config_file.exists():
        typer.echo(f"Claude config file not found at: {config_file}")
        return

    try:
        # Read current config
        with open(config_file) as f:
            config = json.load(f)

        # Check if mcpServers exists and server is in it
        if "mcpServers" not in config or server_name not in config["mcpServers"]:
            typer.echo(f"Server {server_name} is not installed in Claude config")
            return

        # Remove the server config
        del config["mcpServers"][server_name]

        # Write updated config
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        typer.echo(f"Successfully removed {server_name} from Claude config")

    except Exception as e:
        typer.echo(f"Error updating Claude config: {str(e)}")
        return


def main():
    app()
