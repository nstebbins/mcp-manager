import copy
import json
import os
from enum import Enum
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .dependency_checker import check_dependencies
from .server_registry import (
    get_config_path,
    get_installed_servers,
    get_mcp_config,
    get_server_info,
    search_servers,
)

app = typer.Typer()
config_app = typer.Typer()
app.add_typer(config_app, name="config", help="Manage client configuration")

console = Console()


class ClientType(str, Enum):
    CURSOR = "cursor"
    CLAUDE = "claude"


# Define options at module level
client_option = typer.Option(ClientType.CLAUDE, help="Client type (cursor or claude)")


@app.command()
def search(keyword: str):
    """
    Search the online registry for servers matching the keyword.
    """
    matches = search_servers(keyword)
    if not matches:
        console.print(f"[red]No servers found matching:[/red] {keyword}")
        return

    table = Table(
        title=f"Found {len(matches)} matching servers", show_header=True, header_style="bold magenta"
    )
    table.add_column("Server", style="cyan")
    table.add_column("Description")
    table.add_column("Maintainer", style="green")

    for server_name in matches:
        info = get_server_info(server_name)
        table.add_row(server_name, info.description, info.maintainer)

    console.print(table)


@app.command()
def info(server_name: str):
    """
    Display detailed information about a specific server.
    """
    server_info = get_server_info(server_name)
    if not server_info:
        console.print(f"[red]Server not found:[/red] {server_name}")
        return

    panel = Panel.fit(
        f"[bold cyan]Server:[/bold cyan] {server_name}\n"
        f"[bold]Description:[/bold] {server_info.description}\n"
        f"[bold green]Maintainer:[/bold green] {server_info.maintainer}",
        title="Server Information",
        border_style="blue",
    )
    console.print(panel)

    if server_info.required_config:
        config_table = Table(title="Required Configuration", show_header=False, box=None)
        for config in server_info.required_config:
            config_table.add_row("•", config)
        console.print(config_table)

    if server_info.dependencies:
        dep_table = Table(title="Dependencies", show_header=False, box=None)
        for dep in server_info.dependencies:
            dep_table.add_row("•", dep)
        console.print(dep_table)


@app.command()
def install(
    server_name: str,
    client: Optional[ClientType] = client_option,
):
    """
    Install a server for the specified client.
    """
    server_info = get_server_info(server_name)
    if not server_info:
        console.print(f"[red]Server not found:[/red] {server_name}")
        return

    dependencies = server_info.dependencies
    if dependencies:
        all_installed, missing_deps = check_dependencies(dependencies)
        if not all_installed:
            console.print("[red]Missing required dependencies:[/red]")
            for dep in missing_deps:
                console.print(f"• {dep}")
            console.print("\n[yellow]Please install the missing dependencies and try again.[/yellow]")
            return

    mcp_config = get_mcp_config(server_name)
    if not mcp_config:
        console.print(f"[red]No MCP configuration available for server:[/red] {server_name}")
        return

    if server_info.requires_user_input and server_info.user_input_prompt:
        user_input = typer.prompt(server_info.user_input_prompt)
        mcp_config = copy.deepcopy(mcp_config)
        mcp_config["args"] = [
            arg.replace("{user_directory}", user_input) if isinstance(arg, str) else arg
            for arg in mcp_config["args"]
        ]

    config_file = get_config_path(client)
    if not config_file.exists():
        console.print(f"[red]Config file not found at:[/red] {config_file}")
        return

    try:
        with open(config_file) as f:
            config = json.load(f)

        if "mcpServers" not in config:
            config["mcpServers"] = {}

        config["mcpServers"][server_name] = mcp_config

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        console.print(f"[green]Successfully installed[/green] {server_name} for {client.value}")

    except Exception as e:
        console.print(f"[red]Error updating {client.value} config:[/red] {str(e)}")
        return


@app.command()
def uninstall(
    server_name: str,
    client: Optional[ClientType] = client_option,
):
    """
    Remove a server from the client configuration.
    """
    config_file = get_config_path(client)

    if not config_file.exists():
        console.print(f"[red]Config file not found at:[/red] {config_file}")
        return

    try:
        with open(config_file) as f:
            config = json.load(f)

        if "mcpServers" not in config or server_name not in config["mcpServers"]:
            console.print(f"[red]Server {server_name} is not installed in {client.value} config[/red]")
            return

        del config["mcpServers"][server_name]

        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        console.print(f"[green]Successfully removed[/green] {server_name} from {client.value} config")

    except Exception as e:
        console.print(f"[red]Error updating {client.value} config:[/red] {str(e)}")
        return


@config_app.command("path")
def config_path(client: Optional[ClientType] = client_option):
    """
    Show current client config file path.
    """
    config_file = get_config_path(client)
    console.print(f"Current {client.value} config path: {config_file}")
    console.print(f"Config exists: {config_file.exists()}")


@config_app.command("set-path")
def set_config_path(new_path: str, client: Optional[ClientType] = client_option):
    """
    Set a new path for the client config file.
    """
    new_path = Path(os.path.expanduser(new_path))

    # Ensure the directory exists
    new_path.parent.mkdir(parents=True, exist_ok=True)

    # If old config exists, copy it to new location
    old_config = get_config_path(client)
    if old_config.exists():
        if new_path.exists():
            overwrite = typer.confirm("Config file already exists at new location. Overwrite?")
            if not overwrite:
                console.print("Operation cancelled")
                return
        with old_config.open() as f:
            config = json.load(f)
        with new_path.open("w") as f:
            json.dump(config, f, indent=2)

    # Store the custom path in user's home directory
    custom_path_file = Path(os.path.expanduser(f"~/.mcp_manager_{client.value}_config"))
    with custom_path_file.open("w") as f:
        f.write(str(new_path))

    console.print(f"[green]Successfully set new {client.value} config path to:[/green] {new_path}")


@app.command()
def list(client: Optional[ClientType] = client_option):
    """
    List all installed MCP servers.
    """
    installed_servers = get_installed_servers(client)

    if not installed_servers:
        console.print(f"[yellow]No MCP servers are currently installed for {client.value}.[/yellow]")
        return

    table = Table(
        title=f"Installed MCP Servers for {client.value}", show_header=True, header_style="bold magenta"
    )
    table.add_column("Server Name", style="cyan")
    table.add_column("Description")
    table.add_column("Maintainer", style="green")

    for server in installed_servers:
        table.add_row(server["name"], server["description"], server["maintainer"])

    console.print(table)


def main():
    app()
