"""Test CLI functionality across platforms."""

import subprocess
import sys


def test_cli_help():
    """Test that CLI help command works."""
    result = subprocess.run(
        [sys.executable, "-m", "lazydjango", "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "lazydjango" in result.stdout.lower()


def test_cli_import():
    """Test that lazydjango can be imported."""
    import lazydjango

    assert lazydjango is not None


def test_cli_module():
    """Test that CLI module exists."""
    from lazydjango import cli

    assert hasattr(cli, "main")
