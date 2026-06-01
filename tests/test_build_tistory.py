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
        assert len(html_files) == 0, (
            f"Dry-run should not write files, found {len(html_files)}"
        )
        assert "Built" in result.stdout


def test_build_publish_without_mmdc():
    """--publish should fail if mmdc is not available (simulated via PATH)."""
    import shutil

    if shutil.which("mmdc"):
        # mmdc is installed, skip this test
        return
    result = run_build("--all", "--publish", "--dry-run")
    assert result.returncode != 0, "--publish should fail without mmdc"
    assert "mmdc" in result.stdout.lower() or "mmdc" in result.stderr.lower()


# --- Fallback mode tests ---


def test_fallback_list_wrapping():
    """Fallback converter wraps <li> elements in <ul>."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from build_tistory import fallback_convert

    md = "- item one\n- item two\n- item three"
    html = fallback_convert(md)
    assert "<ul>" in html, f"Missing <ul> wrapper: {html}"
    assert "</ul>" in html, f"Missing </ul> closer: {html}"
    assert html.index("<ul>") < html.index("<li>"), "ul must come before first li"
    assert html.index("</ul>") > html.rindex("</li>"), "ul must close after last li"
    # No bare <li> without <ul>
    lines = html.split("\n")
    li_lines = [l for l in lines if "<li>" in l]
    assert len(li_lines) == 3


def test_fallback_list_interrupted():
    """Fallback converter closes <ul> when list is interrupted by non-list content."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from build_tistory import fallback_convert

    md = "- item one\n- item two\n\nSome paragraph\n\n- new list"
    html = fallback_convert(md)
    # Should have two separate <ul> blocks
    assert html.count("<ul>") == 2, f"Expected 2 <ul> blocks: {html}"
    assert html.count("</ul>") == 2, f"Expected 2 </ul> closers: {html}"


def test_fallback_link_conversion():
    """Fallback converter converts markdown links to <a> tags."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from build_tistory import fallback_convert

    md = "See [주식](../level-01-basic/stock.md) for details."
    html = fallback_convert(md)
    assert '<a href="../level-01-basic/stock.md">주식</a>' in html, (
        f"Link not converted: {html}"
    )


def test_fallback_link_rewriting_integration():
    """Full pipeline rewrites fallback-converted links to Tistory URLs."""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from build_tistory import fallback_convert, rewrite_md_links

    md = "- [주식](../level-01-basic/stock.md)\n- [채권](../level-02-price/bond.md)"
    html = fallback_convert(md)
    html = rewrite_md_links(html)
    assert "stockvisualnote.tistory.com/entry/stock" in html, (
        f"Link not rewritten: {html}"
    )
    assert "stockvisualnote.tistory.com/entry/bond" in html, (
        f"Link not rewritten: {html}"
    )
    assert "<ul>" in html


if __name__ == "__main__":
    test_build_single_file()
    test_build_help()
    print("All smoke tests passed!")
