"""
Server registry containing information about available MCP servers.
Each server entry contains:
- description: A brief description of what the server does
- maintainer: Who maintains this server
- claude_config: The configuration needed for Claude settings file
- required_config: Any additional configuration needed
- dependencies: List of dependencies required
"""

import os
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ClaudeConfig(BaseModel):
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None

    class Config:
        json_encoders = {dict: lambda v: v or None}

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if data.get("env") is None:
            del data["env"]
        return data


class MCPServer(BaseModel):
    description: str
    maintainer: str
    claude_config: ClaudeConfig
    required_config: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    requires_user_input: bool = False
    user_input_prompt: Optional[str] = None


MCP_SERVERS: Dict[str, MCPServer] = {
    "filesystem": MCPServer(
        description="MCP server for filesystem operations",
        maintainer="Anthropic",
        claude_config=ClaudeConfig(
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
        claude_config=ClaudeConfig(
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
        claude_config=ClaudeConfig(
            command="docker",
            args=["run", "-i", "--rm", "mcp/fetch"],
        ),
        required_config=[],
        dependencies=["Docker"],
    ),
    "git": MCPServer(
        description="MCP server for Git operations",
        maintainer="MCP",
        claude_config=ClaudeConfig(
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


def get_claude_config(server_name: str) -> Optional[Dict]:
    """
    Get the Claude configuration for a specific server.

    Args:
        server_name: Name of the server to get config for

    Returns:
        Claude configuration dictionary if found, None otherwise
    """
    server_info = get_server_info(server_name)
    if not server_info:
        return None
    return server_info.claude_config.model_dump(exclude_none=True)
