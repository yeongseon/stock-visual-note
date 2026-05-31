#!/usr/bin/env python3
"""Build Tistory-ready HTML from markdown articles.

Usage:
    python3 scripts/build_tistory.py content/.../stock.md     # single file
    python3 scripts/build_tistory.py --all --status published # all published
    python3 scripts/build_tistory.py --output-dir dist/       # output directory

Output: HTML file ready for Tistory editor (HTML mode paste).
"""

import argparse
import re
import sys
import yaml
from pathlib import Path

try:
    import markdown

    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False

CONTENT_ROOT = Path(__file__).parent.parent / "content"
DEFAULT_OUTPUT = Path(__file__).parent.parent / "dist"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse YAML frontmatter and return (metadata, body)."""
    match = re.match(r"^---\n(.*?\n)---\n(.*)$", text, re.DOTALL)
    if not match:
        return {}, text
    fm = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    return fm, body


def markdown_to_html(body: str) -> str:
    """Convert markdown body to HTML."""
    if HAS_MARKDOWN:
        return markdown.markdown(
            body,
            extensions=["tables", "fenced_code", "toc"],
            output_format="html5",
        )
    # Fallback: basic conversion without library
    return fallback_convert(body)


def fallback_convert(body: str) -> str:
    """Minimal markdown-to-HTML without external libraries."""
    lines = body.split("\n")
    html_lines = []
    in_code = False
    in_table = False

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
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        # Table rows
        elif line.startswith("|"):
            if "|---" in line or "| ---" in line:
                continue  # skip separator
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
            # Blockquotes
            if line.startswith("> "):
                html_lines.append(f"<blockquote>{line[2:]}</blockquote>")
            elif line.startswith("- "):
                html_lines.append(f"<li>{line[2:]}</li>")
            elif line.strip():
                html_lines.append(f"<p>{line}</p>")

    if in_table:
        html_lines.append("</table>")

    return "\n".join(html_lines)


def build_tistory_html(filepath: Path) -> str:
    """Build full Tistory HTML from a markdown file."""
    text = filepath.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(text)

    html_body = markdown_to_html(body)

    # Wrap with Tistory-friendly structure
    title = fm.get("title", "Untitled")
    tags = fm.get("tags", [])
    description = fm.get("description", "")

    html = f"""<!-- 
  Title: {title}
  Description: {description}
  Tags: {", ".join(tags)}
-->
<div class="stock-visual-note">
{html_body}
</div>
"""
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
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
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
        out_path = output_dir / filepath.with_suffix(".html").name
        out_path.write_text(html, encoding="utf-8")
        built += 1

    print(f"Built {built} HTML files → {output_dir}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
