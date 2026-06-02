#!/usr/bin/env python3
"""Build Tistory-ready HTML from markdown articles.

Usage:
    python3 scripts/build_tistory.py content/.../stock.md     # single file
    python3 scripts/build_tistory.py --all --status published # all published
    python3 scripts/build_tistory.py --output-dir dist/       # output directory
    python3 scripts/build_tistory.py --all --dry-run          # preview without writing

Output: HTML file ready for Tistory editor (HTML mode paste).
Mermaid blocks are rendered as inline SVG (requires mmdc CLI).
"""

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import yaml
from pathlib import Path

try:
    import markdown

    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

CONTENT_ROOT = Path(__file__).parent.parent / "content"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "dist"

# Tistory URL mapping: slug -> full URL
TISTORY_BASE = "https://stockvisualnote.tistory.com"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter and return (metadata, body)."""
    match = re.match(r"^---\n(.*?\n)---\n(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    fm = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    return fm, body


def has_mmdc() -> bool:
    """Check if mermaid-cli (mmdc) is available."""
    return shutil.which("mmdc") is not None


def render_mermaid_svg(mermaid_code: str) -> str | None:
    """Render Mermaid code to SVG string using mmdc CLI."""
    if not has_mmdc():
        return None

    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
        f.write(mermaid_code)
        input_path = f.name

    output_path = input_path.replace(".mmd", ".svg")
    try:
        result = subprocess.run(
            [
                "mmdc",
                "-i",
                input_path,
                "-o",
                output_path,
                "--backgroundColor",
                "transparent",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and Path(output_path).exists():
            svg = Path(output_path).read_text(encoding="utf-8")
            return svg
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    finally:
        Path(input_path).unlink(missing_ok=True)
        Path(output_path).unlink(missing_ok=True)

    return None


def rewrite_md_links(html: str) -> str:
    """Strip internal .md links, keeping only the link text.

    Pattern: <a href="...slug.md">텍스트</a> -> 텍스트
    """
    return re.sub(r'<a href="[^"]*\.md">([^<]+)</a>', r"\1", html)


def markdown_to_html(body: str) -> str:
    """Convert markdown body to HTML with Mermaid SVG rendering."""

    # Extract and render mermaid blocks before markdown conversion
    def mermaid_replacer(match):
        code = match.group(1)
        svg = render_mermaid_svg(code)
        if svg:
            return f'\n<div class="mermaid-diagram">\n{svg}\n</div>\n'
        # Fallback: keep as code block for client-side rendering
        return f'\n<div class="mermaid">\n{code}\n</div>\n'

    body = re.sub(r"```mermaid\n(.*?)```", mermaid_replacer, body, flags=re.DOTALL)

    if HAS_MARKDOWN:
        html = markdown.markdown(
            body,
            extensions=["tables", "fenced_code", "toc"],
            output_format="html5",
        )
    else:
        html = fallback_convert(body)

    return html


def fallback_convert(body: str) -> str:
    """Minimal markdown-to-HTML without external libraries."""
    # Convert markdown links [text](path.md) to <a> tags first
    body = re.sub(
        r"\[([^\]]+)\]\(([^)]*\.md)\)",
        lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>',
        body,
    )

    lines = body.split("\n")
    html_lines = []
    in_code = False
    in_table = False
    in_list = False

    for line in lines:
        # Code blocks
        if line.startswith("```"):
            if in_code:
                html_lines.append("</code></pre>")
                in_code = False
            else:
                lang = line[3:].strip()
                html_lines.append(f'<pre><code class="{lang}">')
                in_code = True
            continue

        if in_code:
            html_lines.append(line)
            continue

        # Headings
        if line.startswith("## "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("### "):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append(f"<h3>{line[4:]}</h3>")
        # Table rows
        elif line.startswith("|"):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            if "|---" in line or "| ---" in line:
                continue
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if not in_table:
                html_lines.append("<table>")
                in_table = True
            html_lines.append(
                "<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>"
            )
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
            if line.startswith("> "):
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<blockquote>{line[2:]}</blockquote>")
            elif line.startswith("- "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                html_lines.append(f"<li>{line[2:]}</li>")
            elif line.strip():
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<p>{line}</p>")
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False

    if in_table:
        html_lines.append("</table>")
    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)


def build_tistory_html(filepath: Path) -> str:
    """Build full Tistory HTML from a markdown file."""
    text = filepath.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    html_body = markdown_to_html(body)
    html_body = rewrite_md_links(html_body)

    title = fm.get("title", "Untitled")
    tags = fm.get("tags", [])
    description = fm.get("description", "")

    # Add Mermaid client-side renderer fallback (when mmdc not available)
    mermaid_script = ""
    if '<div class="mermaid">' in html_body:
        mermaid_script = (
            '\n<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>'
            "\n<script>mermaid.initialize({startOnLoad:true});</script>\n"
        )

    html = f"""<!-- 
  Title: {title}
  Description: {description}
  Tags: {", ".join(tags)}
-->
<div class="stock-visual-note">
{html_body}
</div>
{mermaid_script}"""
    return html


def main():
    parser = argparse.ArgumentParser(description="Build Tistory HTML from markdown")
    parser.add_argument("files", nargs="*", help="Markdown files to convert")
    parser.add_argument("--all", action="store_true", help="Convert all articles")
    parser.add_argument(
        "--status", default=None, help="Filter by status (e.g., published)"
    )
    parser.add_argument(
        "--output-dir", default=str(DEFAULT_OUTPUT), help="Output directory"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without writing files"
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish mode: fail if mmdc is not installed (no client-side fallback)",
    )
    args = parser.parse_args()

    # Publish mode: require mmdc for pre-rendered SVG output
    if args.publish and not has_mmdc():
        print("ERROR: --publish requires mmdc (mermaid-cli) to be installed.")
        print("Install with: npm install -g @mermaid-js/mermaid-cli")
        return 1

    output_dir = Path(args.output_dir)
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        files = sorted(CONTENT_ROOT.rglob("*.md"))
    elif args.files:
        files = [Path(f) for f in args.files]
    else:
        parser.print_help()
        return 1

    built = 0
    for filepath in files:
        if not filepath.exists():
            print(f"  ✗ Not found: {filepath}")
            continue

        # Filter by status if specified
        if args.status:
            text = filepath.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(text)
            if fm.get("status") != args.status:
                continue

        html = build_tistory_html(filepath)

        if args.dry_run:
            print(f"  [dry-run] {filepath.name} → {filepath.stem}.html")
        else:
            out_path = output_dir / filepath.with_suffix(".html").name
            out_path.write_text(html, encoding="utf-8")

        built += 1

    print(f"Built {built} HTML files → {output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
