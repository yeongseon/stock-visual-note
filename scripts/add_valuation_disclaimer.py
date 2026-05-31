#!/usr/bin/env python3
"""Add valuation disclaimer to valuation-related articles."""

import sys
from pathlib import Path

CONTENT_ROOT = Path(__file__).parent.parent / "content"

VALUATION_SLUGS = [
    "per",
    "pbr",
    "psr",
    "roe",
    "ev-ebitda",
    "peg",
    "bps",
    "eps",
    "multiple",
]

VALUATION_DISCLAIMER = (
    "> ⚠️ 밸류에이션 지표는 투자 판단의 **참고 자료**일 뿐, "
    "특정 수치가 매수·매도 시점을 의미하지 않습니다. "
    "반드시 다른 지표·정성 분석과 함께 종합적으로 판단하세요."
)


def add_valuation_disclaimer(filepath: Path) -> bool:
    text = filepath.read_text(encoding="utf-8")

    if "밸류에이션 지표는 투자 판단의" in text:
        return False  # already has it

    # Insert before "## 초보자가 자주 하는 오해" section
    marker = "## 초보자가 자주 하는 오해"
    idx = text.find(marker)
    if idx == -1:
        return False

    text = text[:idx] + VALUATION_DISCLAIMER + "\n\n" + text[idx:]
    filepath.write_text(text, encoding="utf-8")
    return True


def main():
    modified = 0
    for slug in VALUATION_SLUGS:
        matches = list(CONTENT_ROOT.rglob(f"{slug}.md"))
        for f in matches:
            if add_valuation_disclaimer(f):
                modified += 1
                print(f"  ✓ {f.relative_to(CONTENT_ROOT.parent)}")

    print(f"\nDone: {modified} files updated with valuation disclaimer.")


if __name__ == "__main__":
    main()
