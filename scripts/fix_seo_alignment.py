#!/usr/bin/env python3
"""Fix SEO alignment: ensure primary_keyword appears in seo_title,
and footer Tags match frontmatter tags."""

import re
import yaml
from pathlib import Path

CONTENT_ROOT = Path(__file__).parent.parent / "content"


def fix_file(filepath: Path) -> list[str]:
    """Fix SEO and tag alignment. Returns list of fixes applied."""
    text = filepath.read_text(encoding="utf-8")
    fixes = []

    fm_match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not fm_match:
        return fixes

    try:
        fm = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError:
        return fixes

    if not isinstance(fm, dict):
        return fixes

    fm_text = fm_match.group(1)
    body = text[fm_match.end() :]
    changed = False

    # Fix 1: Align footer Tags with frontmatter tags
    fm_tags = fm.get("tags", [])
    if fm_tags:
        tags_line_match = re.search(r"^Tags:\s*(.+)$", body, re.MULTILINE)
        if tags_line_match:
            expected_footer = "Tags: " + ", ".join(fm_tags)
            current_footer = tags_line_match.group(0)
            if current_footer != expected_footer:
                body = body.replace(current_footer, expected_footer)
                fixes.append("footer tags aligned")
                changed = True

    # Fix 2: Ensure primary_keyword is in seo_title
    pk = fm.get("primary_keyword", "")
    seo_title = fm.get("seo_title", "")
    if pk and seo_title and pk not in seo_title:
        # Strategy: use a simpler primary_keyword derived from slug/title
        # Or update seo_title to include it
        # Best: simplify primary_keyword to core term
        title = fm.get("title", "")
        # Extract the core keyword (first term, before comma/dash)
        core = title.split(",")[0].split("—")[0].split(" ")[0].strip()
        if core and core in seo_title:
            # Update primary_keyword to the core that's already in seo_title
            old_pk_line = f'primary_keyword: "{pk}"'
            new_pk_line = f'primary_keyword: "{core}"'
            if old_pk_line in fm_text:
                fm_text = fm_text.replace(old_pk_line, new_pk_line)
                fixes.append(f"primary_keyword: '{pk}' → '{core}'")
                changed = True
        else:
            # Fallback: find a word from title that appears in seo_title
            title_words = [w for w in re.split(r"[,\s—\-()（）]", title) if len(w) >= 2]
            for word in title_words:
                if word in seo_title:
                    old_pk_line = f'primary_keyword: "{pk}"'
                    new_pk_line = f'primary_keyword: "{word}"'
                    if old_pk_line in fm_text:
                        fm_text = fm_text.replace(old_pk_line, new_pk_line)
                        fixes.append(f"primary_keyword: '{pk}' → '{word}'")
                        changed = True
                    break

    if changed:
        new_text = f"---\n{fm_text}---\n{body}"
        filepath.write_text(new_text, encoding="utf-8")

    return fixes


def main():
    md_files = sorted(CONTENT_ROOT.rglob("*.md"))
    total_fixes = 0
    for f in md_files:
        fixes = fix_file(f)
        if fixes:
            total_fixes += len(fixes)
            for fix in fixes:
                print(f"  ✓ {f.name}: {fix}")

    print(f"\nTotal fixes: {total_fixes}")


if __name__ == "__main__":
    main()
