#!/usr/bin/env python3
"""Add search_intent and primary_keyword to all article frontmatter.

Derives:
- primary_keyword: from slug (converted to readable Korean where possible) or title
- search_intent: based on topic/level mapping
"""

import re
import sys
import yaml
from pathlib import Path

CONTENT_ROOT = Path(__file__).parent.parent / "content"

INTENT_MAP = {
    "basic": "주식 기초 용어 학습",
    "market-trading": "주식 매매 방법 이해",
    "financial-statements": "재무제표 읽는 법",
    "ratios": "재무비율 분석 방법",
    "valuation": "기업 가치평가 방법",
    "events": "주주환원·이벤트 이해",
    "earnings": "자본변동·공시 이해",
    "industry-macro": "실적·업황 분석",
    "strategy-risk": "투자전략·리스크 이해",
    "company-analysis": "종합 기업분석 방법",
}


def extract_primary_keyword(title: str) -> str:
    """Extract primary keyword from title (first meaningful term)."""
    # Remove common suffixes like "뜻", "이란", etc. to get core keyword
    # Take the part before comma or dash
    core = title.split(",")[0].split("—")[0].split("-")[0].strip()
    # Remove trailing "뜻", "이란" etc.
    core = re.sub(r"\s*(뜻|이란|란)\s*$", "", core)
    return core


def add_seo_fields(filepath: Path) -> bool:
    """Add search_intent and primary_keyword if missing."""
    text = filepath.read_text(encoding="utf-8")

    match = re.match(r"^---\n(.*?\n)---\n", text, re.DOTALL)
    if not match:
        return False

    fm_text = match.group(1)

    # Skip if already has both fields
    if "search_intent:" in fm_text and "primary_keyword:" in fm_text:
        return False

    try:
        fm = yaml.safe_load(fm_text)
    except Exception:
        return False

    rest = text[match.end() :]

    # Add search_intent
    if "search_intent:" not in fm_text:
        topic = fm.get("topic", "basic")
        intent = INTENT_MAP.get(topic, "주식 용어 학습")
        fm_text += f'search_intent: "{intent}"\n'

    # Add primary_keyword
    if "primary_keyword:" not in fm_text:
        title = fm.get("title", fm.get("slug", ""))
        keyword = extract_primary_keyword(title)
        fm_text += f'primary_keyword: "{keyword}"\n'

    new_text = f"---\n{fm_text}---\n{rest}"
    if new_text != text:
        filepath.write_text(new_text, encoding="utf-8")
        return True
    return False


def main():
    md_files = sorted(CONTENT_ROOT.rglob("*.md"))
    modified = 0
    for f in md_files:
        if add_seo_fields(f):
            modified += 1

    print(f"Done: {modified}/{len(md_files)} files updated with SEO fields.")


if __name__ == "__main__":
    main()
