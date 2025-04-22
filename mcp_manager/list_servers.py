#!/usr/bin/env python3
"""
Command-line tool to list installed MCP servers.
"""

import argparse

from server_registry import get_installed_servers


def main():
    parser = argparse.ArgumentParser(description="List installed MCP servers")
    parser.add_argument(
        "--client",
        choices=["claude", "cursor"],
        default="claude",
        help="Client to list servers for (default: claude)",
    )
    args = parser.parse_args()

    installed_servers = get_installed_servers(args.client)

    if not installed_servers:
        print(f"No MCP servers found in {args.client} configuration.")
        return

    print(f"\nInstalled MCP Servers for {args.client}:")
    print("=" * 80)

    for server in installed_servers:
        print(f"\nServer: {server['name']}")
        print(f"Description: {server['description']}")
        print(f"Maintainer: {server['maintainer']}")
        print("-" * 40)


if __name__ == "__main__":
    main()
