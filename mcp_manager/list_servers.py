#!/usr/bin/env python3
"""
Command-line tool to list installed MCP servers.
"""

from server_registry import get_installed_servers


def main():
    installed_servers = get_installed_servers()

    if not installed_servers:
        print("No MCP servers found in Claude configuration.")
        return

    print("\nInstalled MCP Servers:")
    print("=" * 80)

    for server in installed_servers:
        print(f"\nServer: {server['name']}")
        print(f"Description: {server['description']}")
        print(f"Maintainer: {server['maintainer']}")
        print("-" * 40)


if __name__ == "__main__":
    main()
