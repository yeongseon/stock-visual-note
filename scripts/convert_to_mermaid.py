#!/usr/bin/env python3
"""Convert ASCII diagrams to Mermaid syntax across all articles.

Strategy:
- Flowchart (graph TD/LR) for process flows and hierarchies
- Block diagrams for comparisons and structures
- Detects patterns in ASCII and generates appropriate Mermaid

This script replaces the ASCII code block in "## 그림으로 이해하기" sections
with a ```mermaid block.
"""

import re
import sys
from pathlib import Path

CONTENT_ROOT = Path(__file__).parent.parent / "content"


def ascii_to_mermaid(ascii_text: str, slug: str, title: str) -> str:
    """Convert ASCII diagram to Mermaid based on content analysis."""

    # Analyze the ASCII content for patterns
    has_arrow_down = "↓" in ascii_text or "▼" in ascii_text
    has_arrow_right = "→" in ascii_text or "──→" in ascii_text
    has_comparison = ascii_text.count("┌") >= 3  # multiple boxes = comparison
    lines = [l.strip() for l in ascii_text.strip().split("\n") if l.strip()]

    # Pattern: Flow/Cycle (has vertical arrows)
    if has_arrow_down and not has_comparison:
        return build_flowchart(ascii_text, slug)

    # Pattern: Framework with arrows (interpretation guides)
    if has_arrow_right and "──→" in ascii_text:
        return build_framework(ascii_text, slug)

    # Pattern: Comparison (multiple boxes side by side)
    if has_comparison:
        return build_comparison(ascii_text, slug)

    # Default: simple block diagram
    return build_simple(ascii_text, slug, title)


def extract_flow_steps(ascii_text: str) -> list[str]:
    """Extract sequential steps from flow diagrams."""
    steps = []
    for line in ascii_text.split("\n"):
        line = line.strip()
        # Remove box drawing chars
        cleaned = re.sub(r"[┌┐└┘├┤┬┴─│═▼↓↑→←]", "", line).strip()
        cleaned = re.sub(r"^[•·\-\s]+", "", cleaned).strip()
        if (
            cleaned
            and len(cleaned) > 2
            and not cleaned.startswith("┌")
            and "──" not in cleaned
        ):
            # Skip pure decorative lines
            if not all(c in "─═│┌┐└┘├┤┬┴ " for c in line):
                steps.append(cleaned)
    return steps


def build_flowchart(ascii_text: str, slug: str) -> str:
    """Build a vertical flowchart from ASCII with arrows."""
    lines = ascii_text.split("\n")
    steps = []

    for line in lines:
        line_stripped = line.strip()
        # Remove all box-drawing characters
        cleaned = re.sub(r"[┌┐└┘├┤┬┴─│═\s]{2,}", " ", line_stripped)
        cleaned = re.sub(r"^[│┌┐└┘├┤┬┴─═\s]+", "", cleaned)
        cleaned = re.sub(r"[│┌┐└┘├┤┬┴─═\s]+$", "", cleaned)
        cleaned = cleaned.strip()

        # Skip empty, arrow-only, or decorative lines
        if not cleaned or cleaned in ("↓", "▼", "→") or len(cleaned) < 3:
            continue
        if all(c in "─═│┌┐└┘├┤┬┴↓▼→← " for c in cleaned):
            continue

        # Split on arrows to get step relationships
        if "→" in cleaned:
            parts = [p.strip() for p in cleaned.split("→") if p.strip()]
            for p in parts:
                p = re.sub(r"[│┌┐└┘]", "", p).strip()
                if p and len(p) > 1:
                    steps.append(p)
        elif "↓" not in cleaned and "▼" not in cleaned:
            cleaned = re.sub(r"[│┌┐└┘]", "", cleaned).strip()
            if cleaned:
                steps.append(cleaned)

    if len(steps) < 2:
        return build_simple_from_steps(steps, slug)

    # Build mermaid flowchart
    mermaid_lines = ["graph TD"]
    node_ids = []

    for i, step in enumerate(steps):
        node_id = f"A{i}"
        # Escape special characters for mermaid
        safe_step = step.replace('"', "'").replace("(", "（").replace(")", "）")
        mermaid_lines.append(f'    {node_id}["{safe_step}"]')
        node_ids.append(node_id)

    # Connect sequentially
    for i in range(len(node_ids) - 1):
        mermaid_lines.append(f"    {node_ids[i]} --> {node_ids[i + 1]}")

    return "\n".join(mermaid_lines)


def build_framework(ascii_text: str, slug: str) -> str:
    """Build framework/interpretation diagram."""
    lines = ascii_text.split("\n")
    items = []

    for line in lines:
        if "──→" in line or "→" in line:
            # Extract left and right of arrow
            cleaned = re.sub(r"[│┌┐└┘├┤┬┴─═\s]{2,}", " ", line.strip())
            cleaned = re.sub(r"^[│┌┐└┘├┤─═\s]+", "", cleaned).strip()
            cleaned = re.sub(r"[│┌┐└┘]+$", "", cleaned).strip()
            if "→" in cleaned and len(cleaned) > 5:
                parts = cleaned.split("→", 1)
                left = parts[0].strip().strip("─ ")
                right = parts[1].strip() if len(parts) > 1 else ""
                if left and right:
                    items.append((left, right))

    if not items:
        return build_flowchart(ascii_text, slug)

    # Build as flowchart with descriptions
    mermaid_lines = ["graph LR"]
    for i, (left, right) in enumerate(items):
        safe_left = left.replace('"', "'").replace("(", "（").replace(")", "）")
        safe_right = right.replace('"', "'").replace("(", "（").replace(")", "）")
        mermaid_lines.append(f'    L{i}["{safe_left}"] -->|해석| R{i}["{safe_right}"]')

    return "\n".join(mermaid_lines)


def build_comparison(ascii_text: str, slug: str) -> str:
    """Build comparison diagram (two or more items side by side)."""
    lines = ascii_text.split("\n")

    # Extract bullet points grouped by boxes
    groups = []
    current_group = []

    for line in lines:
        cleaned = re.sub(r"[┌┐└┘├┤┬┴─│═]", " ", line).strip()
        cleaned = re.sub(r"\s{2,}", "  ", cleaned)
        if cleaned and len(cleaned) > 2:
            # Check if this starts a new group (has multiple distinct text sections)
            current_group.append(cleaned)

    # Try to extract structured comparison
    # Look for • bullet items
    bullets = []
    for line in lines:
        if "•" in line or "·" in line:
            cleaned = re.sub(r"[┌┐└┘├┤┬┴─│═]", " ", line).strip()
            items = [b.strip() for b in re.split(r"[•·]", cleaned) if b.strip()]
            bullets.extend(items)

    # Look for labeled sections
    sections = []
    current_label = ""
    current_items = []

    for line in lines:
        cleaned = re.sub(r"[┌┐└┘├┤┬┴─│═]", "", line).strip()
        if not cleaned:
            if current_label and current_items:
                sections.append((current_label, current_items[:]))
                current_items = []
                current_label = ""
            continue
        if "•" in cleaned or "·" in cleaned:
            items = [b.strip() for b in re.split(r"[•·]", cleaned) if b.strip()]
            current_items.extend(items)
        elif cleaned and not current_label and len(cleaned) > 2:
            # Could be a section header
            if not any(c in cleaned for c in "→↓▼"):
                current_label = cleaned

    if current_label and current_items:
        sections.append((current_label, current_items))

    if sections and len(sections) >= 2:
        mermaid_lines = ["graph TD"]
        mermaid_lines.append(f'    ROOT(("{slug.upper()}")')
        for i, (label, items) in enumerate(sections):
            safe_label = label.replace('"', "'").replace("(", "（").replace(")", "）")
            node_id = f"G{i}"
            mermaid_lines.append(f'    ROOT --> {node_id}["{safe_label}"]')
            for j, item in enumerate(items[:4]):  # limit items
                safe_item = item.replace('"', "'").replace("(", "（").replace(")", "）")
                mermaid_lines.append(f'    {node_id} --- {node_id}_{j}["{safe_item}"]')
        return "\n".join(mermaid_lines)

    # Fallback: simple flowchart from all meaningful lines
    return build_flowchart(ascii_text, slug)


def build_simple(ascii_text: str, slug: str, title: str) -> str:
    """Build a simple conceptual diagram."""
    lines = ascii_text.split("\n")
    meaningful = []

    for line in lines:
        cleaned = re.sub(r"[┌┐└┘├┤┬┴─│═▼↓↑→←\s]{2,}", " ", line.strip())
        cleaned = cleaned.strip("│┌┐└┘ ")
        if cleaned and len(cleaned) > 3:
            meaningful.append(cleaned)

    if not meaningful:
        return f'graph TD\n    A["{title}"]'

    return build_simple_from_steps(meaningful, slug)


def build_simple_from_steps(steps: list[str], slug: str) -> str:
    """Build simple connected diagram from steps."""
    if not steps:
        return f'graph TD\n    A["{slug}"]'

    mermaid_lines = ["graph TD"]
    for i, step in enumerate(steps[:8]):  # limit nodes
        safe = step.replace('"', "'").replace("(", "（").replace(")", "）")
        mermaid_lines.append(f'    N{i}["{safe}"]')

    for i in range(min(len(steps), 8) - 1):
        mermaid_lines.append(f"    N{i} --> N{i + 1}")

    return "\n".join(mermaid_lines)


def convert_file(filepath: Path) -> bool:
    """Convert ASCII diagram to Mermaid in a single file."""
    text = filepath.read_text(encoding="utf-8")

    # Already has mermaid?
    if "```mermaid" in text:
        return False

    # Find the diagram section
    # Pattern: ## 그림으로 이해하기\n\n```\n...\n```
    pattern = r"(## 그림으로 이해하기\s*\n\s*\n)```\n(.*?)```"
    match = re.search(pattern, text, re.DOTALL)

    if not match:
        return False

    ascii_content = match.group(2)

    # Get slug from frontmatter
    slug_match = re.search(r'^slug:\s*["\']?(\S+)', text, re.MULTILINE)
    slug = slug_match.group(1).strip("\"'") if slug_match else "diagram"

    title_match = re.search(r'^title:\s*["\']?(.+?)["\']\s*$', text, re.MULTILINE)
    title = title_match.group(1) if title_match else slug

    # Convert
    mermaid = ascii_to_mermaid(ascii_content, slug, title)

    # Replace in text
    replacement = f"{match.group(1)}```mermaid\n{mermaid}\n```"
    text = text[: match.start()] + replacement + text[match.end() :]

    filepath.write_text(text, encoding="utf-8")
    return True


def main():
    md_files = sorted(CONTENT_ROOT.rglob("*.md"))
    converted = 0
    failed = []

    for f in md_files:
        try:
            if convert_file(f):
                converted += 1
                print(f"  ✓ {f.relative_to(CONTENT_ROOT.parent)}")
        except Exception as e:
            failed.append((f, str(e)))
            print(f"  ✗ {f.relative_to(CONTENT_ROOT.parent)}: {e}")

    print(f"\nConverted: {converted}/{len(md_files)}")
    if failed:
        print(f"Failed: {len(failed)}")
        for f, e in failed:
            print(f"  - {f.name}: {e}")


if __name__ == "__main__":
    main()
