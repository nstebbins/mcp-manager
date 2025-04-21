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
from typing import Any, Dict, List, Optional

MCP_SERVERS: Dict[str, Dict[str, Any]] = {
    "filesystem": {
        "description": "MCP server for filesystem operations",
        "maintainer": "Anthropic",
        "claude_config": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                os.path.expanduser("~/Documents"),  # Default to user's Documents folder
            ],
        },
        "required_config": ["Allowed directory paths that the server can access"],
        "dependencies": ["Node.js", "npm"],
    }
}


def get_server_info(server_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a specific server.

    Args:
        server_name: Name of the server to look up

    Returns:
        Server information dictionary if found, None otherwise
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
        if keyword in name.lower() or keyword in info["description"].lower():
            matches.append(name)

    return matches


def get_claude_config(server_name: str) -> Optional[Dict[str, Any]]:
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
    return server_info.get("claude_config")
