#!/usr/bin/env python3
"""Fix all Oracle #11 issues: footer, tags, typos."""
import re
from pathlib import Path

CONTENT_DIR = Path("/data/GitHub/stock-visual-note/content/stock-terms/ko")
EXACT_DISCLAIMER = "이 글은 투자 권유가 아니라 주식 용어와 기업분석 방법을 설명하기 위한 교육 콘텐츠입니다. 특정 종목의 매수·매도 판단은 독자 본인의 책임입니다."

# Tag replacements: English -> Korean
TAG_REPLACEMENTS = {
    "KOSDAQ": "코스닥",
    "KOSPI": "코스피",
    "FCF": "잉여현금흐름",
    "CAPEX": "설비투자",
    "ROA": "총자산수익률",
    "ROE": "자기자본수익률",
    "BPS": "주당순자산",
    "PBR": "주가순자산비율",
    "EPS": "주당순이익",
    "PER": "주가수익비율",
    "PSR": "주가매출비율",
    "PEG": "주가수익성장비율",
    "EV/EBITDA": "기업가치배수",
    "EBITDA": "상각전영업이익",
    "CB": "전환사채",
    "BW": "신주인수권부사채",
    "IPO": "기업공개",
    "M&A": "인수합병",
    "YoY": "전년대비",
    "DCA": "분할매수",
    "DRAM": "디램반도체",
    "Python": "파이썬",
    "PER하향": "주가배수하향",
    "PER상향": "주가배수상향",
    "희석EPS": "희석주당순이익",
    "고PER": "고주가배수",
    "저PER": "저주가배수",
    "저PBR": "저주가순자산비율",
}

# Typo fixes
TYPOS = {
    "쌍아둔": "쌓아둔",
    "듀팁분석": "듀퐁분석",
    "듀팁분해": "듀퐁분해",
}

def fix_file(path: Path) -> list[str]:
    changes = []
    text = path.read_text(encoding="utf-8")
    original = text

    # Fix typos
    for wrong, correct in TYPOS.items():
        if wrong in text:
            text = text.replace(wrong, correct)
            changes.append(f"  typo: {wrong} → {correct}")

    # Fix footer: replace *면책 조항: ...* with exact disclaimer
    old_footer = f"*면책 조항: {EXACT_DISCLAIMER}*"
    new_footer = EXACT_DISCLAIMER
    if old_footer in text:
        text = text.replace(old_footer, new_footer)
        changes.append("  footer: removed italic prefix")

    # Fix tags (both frontmatter tags: line and footer Tags: line)
    lines = text.split("\n")
    new_lines = []
    for line in lines:
        # Match frontmatter tags or footer Tags line
        if line.startswith("tags:") or line.startswith("Tags:"):
            prefix = "tags:" if line.startswith("tags:") else "Tags:"
            rest = line[len(prefix):]
            modified = False
            for eng, kor in TAG_REPLACEMENTS.items():
                if eng in rest:
                    rest = rest.replace(eng, kor)
                    modified = True
            if modified:
                new_lines.append(prefix + rest)
                changes.append(f"  tags: converted English to Korean")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
    text = "\n".join(new_lines)

    if text != original:
        path.write_text(text, encoding="utf-8")
    
    # Deduplicate changes
    return list(set(changes))

def main():
    all_files = sorted(CONTENT_DIR.rglob("*.md"))
    total_changed = 0
    for f in all_files:
        changes = fix_file(f)
        if changes:
            total_changed += 1
            print(f"{f.name}: {len(changes)} fix(es)")
            for c in changes:
                print(c)
    print(f"\nTotal files modified: {total_changed}/{len(all_files)}")

if __name__ == "__main__":
    main()
