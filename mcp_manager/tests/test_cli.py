from pathlib import Path
from unittest.mock import patch

import pytest
from syrupy.assertion import SnapshotAssertion
from typer.testing import CliRunner

from mcp_manager.cli import app


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def snapshot(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    return snapshot


@pytest.fixture
def mock_claude_config_path() -> str:
    return str(Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")


@pytest.fixture
def mock_cursor_config_path() -> str:
    return str(Path.home() / ".cursor" / "mcp.json")


@pytest.fixture
def mock_file_operations():
    with patch("pathlib.Path.exists") as mock_exists, patch("pathlib.Path.resolve") as mock_resolve:
        mock_exists.return_value = True
        mock_resolve.return_value = Path("/mock/path")
        yield {"exists": mock_exists, "resolve": mock_resolve}


def test_search_command_with_match(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test the search command with matching keyword"""
    result = runner.invoke(app, ["search", "file"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_search_command_no_match(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test searching for non-existent server"""
    result = runner.invoke(app, ["search", "nonexistent"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_info_command_existing(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test getting info for existing server"""
    result = runner.invoke(app, ["info", "filesystem"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_info_command_nonexisting(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test getting info for non-existing server"""
    result = runner.invoke(app, ["info", "nonexistent"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_info_command_playwright(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test getting info for Playwright server"""
    result = runner.invoke(app, ["info", "playwright"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_install_command_nonexisting(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test installing a non-existing server"""
    result = runner.invoke(app, ["install", "nonexistent"])
    assert result.exit_code == 0
    assert result.output == snapshot


@patch("shutil.which")
def test_dependency_check_playwright(
    mock_which,
    mock_file_operations,
    runner: CliRunner,
    snapshot: SnapshotAssertion,
    mock_claude_config_path: str,
) -> None:
    """Test dependency checking for Playwright server"""
    mock_file_operations["resolve"].return_value = Path(mock_claude_config_path)

    # Mock custom path file to not exist
    custom_path = Path(Path.home() / ".mcp_manager_claude_config")
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.side_effect = lambda p: isinstance(p, Path) and str(p) != str(custom_path)
        # Mock Node.js and npm as not installed
        mock_which.side_effect = lambda cmd: None if cmd in ["node", "npm"] else "/usr/bin/" + cmd

        result = runner.invoke(app, ["install", "playwright", "--client", "claude"])
        assert result.exit_code == 0
        assert "Missing required dependencies" in result.output
        assert result.output == snapshot


def test_set_config_path_command(runner: CliRunner) -> None:
    """Test setting config path"""
    new_path = "/tmp/test_config.json"
    with patch("pathlib.Path.exists") as mock_exists, patch("builtins.open"):
        mock_exists.return_value = False
        result = runner.invoke(app, ["config", "set-path", new_path])
        assert result.exit_code == 0
        assert f"Successfully set new claude config path to: {new_path}" in result.output


def test_set_config_path_command_cursor(runner: CliRunner) -> None:
    """Test setting config path for Cursor"""
    new_path = "/tmp/test_cursor_config.json"
    with patch("pathlib.Path.exists") as mock_exists, patch("builtins.open"):
        mock_exists.return_value = False
        result = runner.invoke(app, ["config", "set-path", new_path, "--client", "cursor"])
        assert result.exit_code == 0
        assert f"Successfully set new cursor config path to: {new_path}" in result.output
