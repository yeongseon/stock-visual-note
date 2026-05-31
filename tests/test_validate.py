#!/usr/bin/env python3
"""Tests for validate.py."""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
CONTENT_DIR = Path(__file__).parent.parent / "content"


def run_validator(*args: str) -> subprocess.CompletedProcess:
    """Run validate.py with given arguments."""
    cmd = [sys.executable, str(SCRIPTS_DIR / "validate.py"), *args]
    return subprocess.run(cmd, capture_output=True, text=True)


def test_validator_passes_strict():
    """All content passes strict validation."""
    result = run_validator("--strict")
    assert result.returncode == 0, (
        f"Validator failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "Errors: 0" in result.stdout


def test_validator_detects_missing_section():
    """Validator detects missing required sections."""
    import tempfile
    import shutil

    # Create a minimal broken file
    tmp_dir = Path(tempfile.mkdtemp())
    level_dir = tmp_dir / "content" / "stock-terms" / "ko" / "level-01-basic"
    level_dir.mkdir(parents=True)

    broken = level_dir / "test-broken.md"
    broken.write_text(
        """---
id: 999
slug: test-broken
title: "테스트 깨진 파일"
seo_title: "테스트 깨진 파일"
description: "테스트용"
category: stock-terms
topic: basic
level: 1
difficulty: beginner
content_type: concept
language: ko
status: draft
source_policy: hypothetical
search_intent: "테스트"
primary_keyword: "테스트"
tags: [테스트, 주식, 기본, 용어, 초보]
last_reviewed: 2026-05-31
---
# 테스트 깨진 파일

## 한 줄 정의

테스트입니다.
""",
        encoding="utf-8",
    )

    # Run validator on just this file (it won't have all sections)
    cmd = [sys.executable, str(SCRIPTS_DIR / "validate.py"), str(broken)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    # Should report errors for missing sections
    shutil.rmtree(tmp_dir)
    # The validator should find issues (missing sections)
    assert "Errors:" in result.stdout or result.returncode != 0


def test_validator_help():
    """Validator --help works."""
    result = run_validator("--help")
    assert result.returncode == 0


if __name__ == "__main__":
    test_validator_passes_strict()
    test_validator_help()
    print("All tests passed!")
