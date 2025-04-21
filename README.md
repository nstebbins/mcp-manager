# MCP Manager

<div align="center">

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](https://pypi.org/project/mcp-manager/)
[![Python](https://img.shields.io/badge/python-^3.12-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A powerful CLI tool for managing Model Context Protocol (MCP) servers. Seamlessly install, configure, and manage MCP servers for AI tools and services.

[Installation](#installation) • [Quick Start](#quick-start) • [Available Servers](#available-servers) • [Development](#development)

</div>

## 🚀 Quick Start

```bash
# Install the package
pip install mcp-manager

# Search for available servers
mcp-manager search browser
# Output:
#   Found 1 matching servers:
#   playwright:
#     Description: MCP server for browser automation with Playwright
#     Maintainer: Anthropic

# Get detailed server information
mcp-manager info playwright
# Output:
#   Server: playwright
#   Description: MCP server for browser automation with Playwright
#   Maintainer: Anthropic
#   Dependencies:
#   - Node.js
#   - npm

# Install a server
mcp-manager install playwright --client=claude
# Output: Successfully installed playwright for Claude
```

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `search <keyword>` | Search for available MCP servers matching the keyword |
| `info <server-name>` | Display detailed information about a specific server |
| `install <server-name> [--client=claude]` | Install an MCP server for a specific client |
| `uninstall <server-name> [--client=claude]` | Remove an installed server |

## 🔌 Available Servers

| Server | Description | Dependencies |
|--------|-------------|--------------|
| **Playwright** | Browser automation server for web interactions | Node.js, npm |
| **Filesystem** | File system operations server for local file access | Node.js, npm |
| **Fetch** | Server for making HTTP requests | Docker |
| **Git** | Server for Git operations | Docker |

## 🎯 Features

- 🔍 Smart server discovery and search
- 🔒 Secure configuration management
- 🔄 Automatic dependency checking
- 🛡️ Client-specific installation options
- 📝 Detailed server information and documentation

## 💻 Installation

For users:
```bash
pip install mcp-manager
```

For developers:
```bash
# Clone the repository
git clone https://github.com/yourusername/mcp-manager.git
cd mcp-manager

# Install dependencies and development tools
poetry install
pre-commit install  # Install git hooks
```

## 🔧 Development

This project leverages modern Python tools and practices:

- **Poetry** - Dependency management and packaging
- **Typer** - CLI interface framework
- **Pydantic** - Data validation
- **Ruff** - Lightning-fast Python linter and formatter
- **Pre-commit** - Git hooks for code quality

### Code Quality

We maintain high code quality standards through automated checks:

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Format code
poetry run ruff format .

# Run linter
poetry run ruff check .

# Run tests
poetry run pytest
```

### 🧪 Testing

The project uses pytest for testing. Run the test suite with:

```bash
poetry run pytest
```

## 📦 Client Support

Currently supports:
- ✅ Claude (primary client)
- 🔄 Additional client support coming soon

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
