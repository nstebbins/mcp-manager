# Getting Started with MCP Manager

## Installation

### Using pip (Recommended)
```bash
pip install mcp-manager
```

### From Source
```bash
git clone https://github.com/nstebbins/mcp-manager.git
cd mcp-manager
poetry install
```

## First Steps

### 1. Search for Servers
```bash
mcp-manager search browser
```

### 2. Get Server Information
```bash
mcp-manager info playwright
```

### 3. Install a Server
```bash
mcp-manager install playwright --client=cursor
```

### 4. Verify Installation
```bash
mcp-manager list
```

## Next Steps

Read about [Core Concepts](./core-concepts.md) to understand MCP architecture
