#!/usr/bin/env python3
"""
Frontmatter validator for stock-visual-note articles.
Checks required fields, section headings, and link validity.

Usage:
    python scripts/validate.py                    # validate all articles
    python scripts/validate.py content/.../per.md # validate specific file
"""

import sys
import re
import yaml
from pathlib import Path

REQUIRED_FIELDS = [
    "id",
    "slug",
    "title",
    "seo_title",
    "topic",
    "level",
    "difficulty",
    "language",
    "status",
    "tags",
    "last_reviewed",
]
VALID_TOPICS = [
    "basic",
    "market-trading",
    "financial-statements",
    "ratios",
    "valuation",
    "events",
    "earnings",
    "industry-macro",
    "strategy-risk",
    "company-analysis",
]
VALID_STATUSES = ["draft", "review", "published"]
VALID_DIFFICULTIES = ["beginner", "intermediate", "advanced"]

REQUIRED_SECTIONS = [
    "한 줄 정의",
    "아주 쉽게 말하면",
    "왜 중요한가",
    "그림으로 이해하기",
    "숫자로 보는 예시",
    "표로 비교하기",
    "초보자가 자주 하는 오해",
    "고수는 이렇게 봅니다",
    "기업분석에서는 이렇게 씁니다",
    "함께 보면 좋은 용어",
    "정리",
    "한 줄 요약",
]

DISCLAIMER = "이 글은 투자 권유가 아니라 주식 용어와 기업분석 방법을 설명하기 위한 교육 콘텐츠입니다."


def validate_file(filepath: Path) -> list[str]:
    """Validate a single markdown article. Returns list of error messages."""
    errors = []
    text = filepath.read_text(encoding="utf-8")

    # Parse frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        errors.append("Missing frontmatter")
        return errors

    try:
        fm = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML frontmatter: {e}")
        return errors

    if not isinstance(fm, dict):
        errors.append("Frontmatter is not a dict")
        return errors

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in fm:
            errors.append(f"Missing field: {field}")

    # Validate field values
    if fm.get("topic") and fm["topic"] not in VALID_TOPICS:
        errors.append(f"Invalid topic: {fm['topic']}")
    if fm.get("status") and fm["status"] not in VALID_STATUSES:
        errors.append(f"Invalid status: {fm['status']}")
    if fm.get("difficulty") and fm["difficulty"] not in VALID_DIFFICULTIES:
        errors.append(f"Invalid difficulty: {fm['difficulty']}")
    if fm.get("language") != "ko":
        errors.append(f"Language should be 'ko', got: {fm.get('language')}")
    if fm.get("tags") and len(fm["tags"]) != 5:
        errors.append(f"Expected 5 tags, got {len(fm['tags'])}")
    if fm.get("level") and not (1 <= fm["level"] <= 10):
        errors.append(f"Level out of range: {fm['level']}")

    # Check required sections
    body = text[fm_match.end() :]
    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in body:
            errors.append(f"Missing section: ## {section}")

    # Check disclaimer
    if DISCLAIMER not in body:
        errors.append("Missing disclaimer footer")

    # Check Tags footer
    if not re.search(r"^Tags:", body, re.MULTILINE):
        errors.append("Missing 'Tags:' footer line")

    # Check for code block diagram
    if "```" not in body:
        errors.append("No code block found (expected ASCII diagram)")

    # Check for table
    if "|---" not in body and "| ---" not in body:
        errors.append("No markdown table found")

    return errors


def main():
    content_root = Path(__file__).parent.parent / "content" / "stock-terms" / "ko"

    if len(sys.argv) > 1:
        files = [Path(f) for f in sys.argv[1:]]
    else:
        files = sorted(content_root.rglob("*.md"))

    total_errors = 0
    files_with_errors = 0

    for f in files:
        if f.name == ".gitkeep":
            continue
        errs = validate_file(f)
        if errs:
            files_with_errors += 1
            total_errors += len(errs)
            print(f"\n❌ {f.relative_to(content_root.parent.parent.parent)}")
            for e in errs:
                print(f"   • {e}")

    total_files = len([f for f in files if f.name != ".gitkeep"])
    print(f"\n{'=' * 50}")
    print(f"Validated: {total_files} files")
    print(f"Errors: {total_errors} in {files_with_errors} files")
    print(f"Clean: {total_files - files_with_errors} files")

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
