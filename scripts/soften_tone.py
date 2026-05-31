#!/usr/bin/env python3
"""Soften assertive investment language across all articles.

Replacements are context-aware: only changes assertive/definitive tone
to softer educational framing.
"""

import re
import sys
from pathlib import Path

CONTENT_ROOT = Path(__file__).parent.parent / "content"

# (pattern, replacement) pairs — order matters for overlapping patterns
REPLACEMENTS = [
    # "악재입니다" → softer
    ("악재입니다", "악재로 해석되는 경우가 많습니다"),
    # "고평가입니다" → softer
    ("고평가입니다", "고평가로 볼 수 있습니다"),
    # "저평가입니다" → softer
    ("저평가입니다", "저평가로 볼 수 있습니다"),
    # "매수 기회가 되기도" is already soft — skip
    # "좋은 매수 기회를 찾을 수 있습니다" → softer
    (
        "좋은 매수 기회를 찾을 수 있습니다",
        "상대적으로 저렴한 구간인지 검토해볼 수 있습니다",
    ),
    # "매수 기회, 상단이면 차익 실현을 검토합니다" → softer
    (
        "하단에 있으면 매수 기회, 상단이면 차익 실현을 검토합니다",
        "하단에 있으면 저평가 가능성을, 상단이면 고평가 가능성을 검토합니다",
    ),
]


def soften_file(filepath: Path) -> bool:
    """Apply softening replacements. Returns True if modified."""
    original = filepath.read_text(encoding="utf-8")
    text = original

    for pattern, replacement in REPLACEMENTS:
        text = text.replace(pattern, replacement)

    if text != original:
        filepath.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    md_files = sorted(CONTENT_ROOT.rglob("*.md"))
    modified = 0
    for f in md_files:
        if soften_file(f):
            modified += 1
            print(f"  ✓ {f.relative_to(CONTENT_ROOT.parent)}")

    print(f"\nDone: {modified}/{len(md_files)} files softened.")


if __name__ == "__main__":
    main()
