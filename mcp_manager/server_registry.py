"""
Server registry containing information about available MCP servers.
Each server entry contains:
- description: A brief description of what the server does
- maintainer: Who maintains this server
- claude_config: The configuration needed for Claude settings file
- required_config: Any additional configuration needed
- dependencies: List of dependencies required
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class MCPConfig(BaseModel):
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None

    model_config = ConfigDict(json_encoders={dict: lambda v: v or None})

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if "env" in data and data["env"] is None:
            del data["env"]
        return data


class MCPServer(BaseModel):
    description: str
    maintainer: str
    mcp_config: MCPConfig
    required_config: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    requires_user_input: bool = False
    user_input_prompt: Optional[str] = None


MCP_SERVERS: Dict[str, MCPServer] = {
    "filesystem": MCPServer(
        description="MCP server for filesystem operations",
        maintainer="Anthropic",
        mcp_config=MCPConfig(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                os.path.expanduser("~/Documents"),  # Default to user's Documents folder
            ],
        ),
        required_config=["Allowed directory paths that the server can access"],
        dependencies=["Node.js", "npm"],
    ),
    "playwright": MCPServer(
        description="MCP server for browser automation with Playwright",
        maintainer="Anthropic",
        mcp_config=MCPConfig(
            command="npx",
            args=["@playwright/mcp@latest"],
            env={"PLAYWRIGHT_DEBUG": "1"},
        ),
        required_config=[],
        dependencies=["Node.js", "npm"],
    ),
    "fetch": MCPServer(
        description="MCP server for making HTTP requests",
        maintainer="MCP",
        mcp_config=MCPConfig(
            command="docker",
            args=["run", "-i", "--rm", "mcp/fetch"],
        ),
        required_config=[],
        dependencies=["Docker"],
    ),
    "memory": MCPServer(
        description="MCP server for managing Claude's memory",
        maintainer="MCP",
        mcp_config=MCPConfig(
            command="docker",
            args=["run", "-i", "-v", "claude-memory:/app/dist", "--rm", "mcp/memory"],
        ),
        required_config=[],
        dependencies=["Docker"],
    ),
    "git": MCPServer(
        description="MCP server for Git operations",
        maintainer="MCP",
        mcp_config=MCPConfig(
            command="docker",
            args=[
                "run",
                "--rm",
                "-i",
                "--mount",
                "type=bind,src={user_directory},dst={user_directory}",
                "mcp/git",
            ],
        ),
        required_config=["Directory path to mount for Git operations"],
        dependencies=["Docker"],
        requires_user_input=True,
        user_input_prompt=(
            "Enter the directory path you want to make available to the MCP Server (absolute path only):"
        ),
    ),
    "github": MCPServer(
        description="MCP server for GitHub operations and API access",
        maintainer="GitHub",
        mcp_config=MCPConfig(
            command="docker",
            args=[
                "run",
                "-i",
                "--rm",
                "-e",
                "GITHUB_PERSONAL_ACCESS_TOKEN",
                "ghcr.io/github/github-mcp-server",
            ],
            env={"GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>"},
        ),
        required_config=["GitHub Personal Access Token with desired permissions"],
        dependencies=["Docker"],
        requires_user_input=True,
        user_input_prompt="Enter your GitHub Personal Access Token (create one at https://github.com/settings/tokens):",
    ),
}


def get_server_info(server_name: str) -> Optional[MCPServer]:
    """
    Get information about a specific server.

    Args:
        server_name: Name of the server to look up

    Returns:
        Server information if found, None otherwise
    """
    return MCP_SERVERS.get(server_name)


def search_servers(keyword: str) -> List[str]:
    """
    Search for servers matching the given keyword.

    Args:
        keyword: Search term to match against server names and descriptions

    Returns:
        List of matching server names
    """
    keyword = keyword.lower()
    matches = []

    for name, info in MCP_SERVERS.items():
        if keyword in name.lower() or keyword in info.description.lower():
            matches.append(name)

    return matches


def get_mcp_config(server_name: str) -> Optional[Dict]:
    """
    Get the MCP configuration for a specific server.

    Args:
        server_name: Name of the server to get config for

    Returns:
        MCP configuration dictionary if found, None otherwise
    """
    server_info = get_server_info(server_name)
    if not server_info:
        return None
    return server_info.mcp_config.model_dump(exclude_none=True)


def get_config_path(client: str = "claude-desktop") -> Path:
    """
    Get the config file path for the specified client.
    """
    # Check for custom path
    custom_path_file = Path(os.path.expanduser(f"~/.mcp_manager_{client}_config"))
    if custom_path_file.exists():
        with custom_path_file.open() as f:
            return Path(f.read().strip())

    # Return default path based on client
    if client == "cursor":
        return Path(os.path.expanduser("~/.cursor/mcp.json"))
    elif client == "claude-code":
        return Path(os.path.expanduser("~/.claude.json"))
    else:  # claude-desktop is default
        return Path(
            os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
        )


def get_installed_servers(client: str = "claude-desktop") -> List[Dict[str, Union[str, Dict]]]:
    """
    Get list of installed MCP servers from client config.
    """
    installed = []
    config_file = get_config_path(client)

    if config_file.exists():
        with open(config_file, "r") as f:
            try:
                config = json.load(f)
                mcp_servers = config.get("mcpServers", {})

                for name, server_config in mcp_servers.items():
                    server_info = get_server_info(name)
                    if server_info:
                        installed.append(
                            {
                                "name": name,
                                "description": server_info.description,
                                "maintainer": server_info.maintainer,
                                "config": server_config,
                            }
                        )
            except json.JSONDecodeError:
                pass

    return installed
