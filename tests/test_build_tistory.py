#!/usr/bin/env python3
"""Smoke tests for build_tistory.py."""

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
CONTENT_DIR = Path(__file__).parent.parent / "content"


def run_build(*args: str) -> subprocess.CompletedProcess:
    """Run build_tistory.py with given arguments."""
    cmd = [sys.executable, str(SCRIPTS_DIR / "build_tistory.py"), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_build_single_file():
    """Build a single article to HTML."""
    sample = next(CONTENT_DIR.rglob("stock.md"))
    with tempfile.TemporaryDirectory() as tmp:
        result = run_build(str(sample), "--output-dir", tmp)
        assert result.returncode == 0, (
            f"Build failed:\n{result.stdout}\n{result.stderr}"
        )
        assert "Built 1" in result.stdout
        html_files = list(Path(tmp).glob("*.html"))
        assert len(html_files) == 1
        content = html_files[0].read_text()
        assert "<div" in content or "<h" in content


def test_build_help():
    """Build --help works."""
    result = run_build("--help")
    assert result.returncode == 0


def test_build_dry_run():
    """Build --dry-run doesn't write files."""
    with tempfile.TemporaryDirectory() as tmp:
        result = run_build("--all", "--output-dir", tmp, "--dry-run")
        assert result.returncode == 0, f"Dry-run failed:\n{result.stderr}"
        html_files = list(Path(tmp).glob("*.html"))
        assert len(html_files) == 0, f"Dry-run should not write files, found {len(html_files)}"
        assert "Built" in result.stdout


if __name__ == "__main__":
    test_build_single_file()
    test_build_help()
    print("All smoke tests passed!")
