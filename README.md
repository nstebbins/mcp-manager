# MCP Manager

A CLI tool for managing MCP servers.

## Installation

```bash
poetry install
pre-commit install  # Install git hooks
```

## Usage

The CLI provides the following commands:

### Search for servers
```bash
mcp-manager search <keyword>
```

### Get server information
```bash
mcp-manager info <server-name>
```

### Install a server
```bash
mcp-manager install <server-name> [--client=cursor|claude] [--scope=global|project]
```

## Development

This project uses:
- Poetry for dependency management
- Typer for CLI interface
- Ruff for linting and formatting
- Pre-commit hooks for automated code quality checks

### Code Quality

The project uses pre-commit hooks to ensure code quality. The hooks will run automatically before each commit, checking for:
- Code formatting (using ruff)
- Code linting (using ruff)
- Common git issues (trailing whitespace, large files, etc.)

To manually run the hooks:
```bash
pre-commit run --all-files
```

To format and lint the code manually:
```bash
poetry run ruff format .
poetry run ruff check .
```
