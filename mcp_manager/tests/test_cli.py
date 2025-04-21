from unittest.mock import mock_open, patch

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


@patch("pathlib.Path.exists")
@patch("builtins.open", new_callable=mock_open, read_data='{"mcpServers": {}}')
def test_install_command_success(
    mock_file, mock_exists, runner: CliRunner, snapshot: SnapshotAssertion
) -> None:
    """Test successful server installation"""
    mock_exists.return_value = True

    result = runner.invoke(app, ["install", "filesystem", "--client", "claude"])
    assert result.exit_code == 0
    assert result.output == snapshot

    # Verify the file was written to
    mock_file.assert_called()
