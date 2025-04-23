# Core Concepts

## What is MCP?

The Model Context Protocol (MCP) is a standardized protocol that enables AI models to interact with external tools and services. It provides a structured way for AI assistants to:
- Access system resources
- Interact with web browsers
- Manage files
- Perform network requests
- Interface with version control systems
- And more...

For more information, see the [MCP specification](https://docs.anthropic.com/en/docs/agents-and-tools/mcp).

## Client-Server Architecture

MCP Manager uses a client-server architecture where:

- **Clients** are the AI tools that use MCP servers.
- **Servers** are the independent processes that provide specific functionality.

Each client has a configuration file that lists the servers it supports.
