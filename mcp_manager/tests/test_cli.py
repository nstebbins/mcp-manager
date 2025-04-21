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
def mock_config_path() -> str:
    return str(Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")


@pytest.fixture
def mock_file_operations():
    with (
        patch("pathlib.Path.exists") as mock_exists,
        patch("pathlib.Path.write_text") as mock_write,
        patch("pathlib.Path.resolve") as mock_resolve,
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        mock_exists.return_value = True
        mock_write.return_value = None
        mock_mkdir.return_value = None

        yield {
            "exists": mock_exists,
            "write_text": mock_write,
            "resolve": mock_resolve,
            "mkdir": mock_mkdir,
        }


def test_search_command_with_match(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test the search command with matching keyword"""
    result = runner.invoke(app, ["search", "file"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_search_command_no_match(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test the search command with non-matching keyword"""
    result = runner.invoke(app, ["search", "nonexistent"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_info_command_existing(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test the info command for existing server"""
    result = runner.invoke(app, ["info", "filesystem"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_info_command_nonexisting(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test the info command for non-existing server"""
    result = runner.invoke(app, ["info", "nonexistent"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_info_command_playwright(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test the info command for Playwright server"""
    result = runner.invoke(app, ["info", "playwright"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_install_command_nonexisting(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test installing a non-existing server"""
    result = runner.invoke(app, ["install", "nonexistent"])
    assert result.exit_code == 0
    assert result.output == snapshot


def test_install_command_unsupported_client(runner: CliRunner, snapshot: SnapshotAssertion) -> None:
    """Test installing with unsupported client type"""
    result = runner.invoke(app, ["install", "filesystem", "--client", "cursor"])
    assert result.exit_code == 0
    assert result.output == snapshot


@patch("shutil.which")
def test_dependency_check_playwright(
    mock_which,
    mock_file_operations,
    runner: CliRunner,
    snapshot: SnapshotAssertion,
    mock_config_path: str,
) -> None:
    """Test dependency checking for Playwright server"""
    mock_file_operations["resolve"].return_value = Path(mock_config_path)

    # Mock custom path file to not exist
    custom_path = Path(Path.home() / ".mcp_manager_config")
    with patch("pathlib.Path.exists") as mock_exists:
        mock_exists.side_effect = lambda p: isinstance(p, Path) and str(p) != str(custom_path)
        # Mock Node.js and npm as not installed
        mock_which.side_effect = lambda cmd: None if cmd in ["node", "npm"] else "/usr/bin/" + cmd

        result = runner.invoke(app, ["install", "playwright", "--client", "claude"])
        assert result.exit_code == 0
        assert "Missing required dependencies" in result.output
        assert result.output == snapshot
