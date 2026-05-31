#!/usr/bin/env python3
"""Batch fix all articles for 20-point improvement plan.

Operations:
1. Remove diagram_required and table_required from frontmatter
2. Add analysis_type: "concept" (or "data-practice" for data-practice articles)
3. Add review_status: "needs_review"
4. Unify footer to: *면책 조항: ...*
5. Add "가상 예시" disclaimer after ## 숫자로 보는 예시 heading
"""

import re
import sys
from pathlib import Path

CONTENT_ROOT = Path(__file__).parent.parent / "content"

DISCLAIMER_SENTENCE = (
    "이 글은 투자 권유가 아니라 주식 용어와 기업분석 방법을 설명하기 위한 "
    "교육 콘텐츠입니다. 특정 종목의 매수·매도 판단은 독자 본인의 책임입니다."
)

UNIFIED_FOOTER = f"*면책 조항: {DISCLAIMER_SENTENCE}*"

HYPOTHETICAL_DISCLAIMER = (
    "> ⚠️ 아래 숫자는 개념 설명을 위한 **가상 예시**이며, 실제 투자 데이터가 아닙니다."
)


def fix_frontmatter(text: str) -> str:
    """Fix frontmatter: remove old fields, add new fields."""
    match = re.match(r"^---\n(.*?\n)---\n", text, re.DOTALL)
    if not match:
        return text

    fm_text = match.group(1)
    rest = text[match.end() :]

    # Remove diagram_required and table_required lines
    fm_text = re.sub(r"^diagram_required:.*\n", "", fm_text, flags=re.MULTILINE)
    fm_text = re.sub(r"^table_required:.*\n", "", fm_text, flags=re.MULTILINE)

    # Determine content_type
    ct_match = re.search(r'^content_type:\s*["\']?([^"\'\n]+)', fm_text, re.MULTILINE)
    content_type = ct_match.group(1).strip() if ct_match else "concept"

    # Add analysis_type if not present
    if "analysis_type:" not in fm_text:
        analysis_type = (
            "data-practice" if content_type == "data-practice" else "concept"
        )
        fm_text += f'analysis_type: "{analysis_type}"\n'

    # Add review_status if not present
    if "review_status:" not in fm_text:
        fm_text += 'review_status: "needs_review"\n'

    return f"---\n{fm_text}---\n{rest}"


def fix_footer(text: str) -> str:
    """Unify footer disclaimer format."""
    # Match various existing footer patterns
    patterns = [
        # *면책 고지: ...*
        r"\*면책 고지:.*?\*",
        # **면책 고지**: ...sentence...
        r"\*\*면책 고지\*\*:.*?" + re.escape("책임입니다."),
        # *면책 조항: ...*  (already correct but re-standardize)
        r"\*면책 조항:.*?\*",
        # Plain text disclaimer (no formatting)
        re.escape(DISCLAIMER_SENTENCE),
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            text = text[: match.start()] + UNIFIED_FOOTER + text[match.end() :]
            return text

    return text


def add_hypothetical_disclaimer(text: str) -> str:
    """Add hypothetical example disclaimer after '## 숫자로 보는 예시' heading."""
    # Skip if already has the disclaimer
    if "가상 예시" in text:
        return text

    marker = "## 숫자로 보는 예시"
    idx = text.find(marker)
    if idx == -1:
        return text

    # Find end of the heading line
    newline_after = text.find("\n", idx)
    if newline_after == -1:
        return text

    # Insert disclaimer after the heading (preserve blank line)
    insert_pos = newline_after + 1
    # Skip any existing blank line
    if insert_pos < len(text) and text[insert_pos] == "\n":
        insert_pos += 1

    text = text[:insert_pos] + HYPOTHETICAL_DISCLAIMER + "\n\n" + text[insert_pos:]
    return text


def process_file(filepath: Path) -> bool:
    """Process a single file. Returns True if modified."""
    original = filepath.read_text(encoding="utf-8")
    text = original

    text = fix_frontmatter(text)
    text = fix_footer(text)
    text = add_hypothetical_disclaimer(text)

    if text != original:
        filepath.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    md_files = sorted(CONTENT_ROOT.rglob("*.md"))
    modified = 0
    for f in md_files:
        if process_file(f):
            modified += 1
            print(f"  ✓ {f.relative_to(CONTENT_ROOT.parent)}")

    print(f"\nDone: {modified}/{len(md_files)} files modified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
