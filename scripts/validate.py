#!/usr/bin/env python3
"""
Frontmatter validator for stock-visual-note articles.
Checks required fields, section headings, link validity, and forbidden expressions.

Usage:
    python scripts/validate.py                    # validate all articles
    python scripts/validate.py content/.../per.md # validate specific file
    python scripts/validate.py --strict           # treat warnings as errors
"""

import sys
import re
import yaml
from pathlib import Path

# --- Schema ---

COMMON_REQUIRED_FIELDS = [
    "id",
    "slug",
    "title",
    "seo_title",
    "description",
    "topic",
    "level",
    "difficulty",
    "content_type",
    "language",
    "status",
    "source_policy",
    "tags",
    "last_reviewed",
]

DATA_PRACTICE_EXTRA_FIELDS = [
    "concept_slug",
    "data_source",
    "data_as_of",
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
VALID_CONTENT_TYPES = ["concept", "data-practice"]
VALID_SOURCE_POLICIES = ["hypothetical", "cited"]

# --- Sections by content type ---

CONCEPT_SECTIONS = [
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

DATA_PRACTICE_SECTIONS = [
    "이 글의 목적",
    "이번 실습에서 확인할 질문",
    "데이터 기준",
    "필요한 라이브러리",
    "데이터 가져오기",
    "계산하기",
    "결과 확인",
    "결과 해석",
    "기업분석에서는 이렇게 씁니다",
    "주의할 점",
    "함께 보면 좋은 글",
    "한 줄 요약",
]

# --- Forbidden expressions (warning) ---

FORBIDDEN_EXPRESSIONS = [
    "무조건 사야",
    "무조건 팔아야",
    "목표가는",
    "목표주가",
    "손해 볼 가능성이 낮",
    "확정 수익",
    "확실하다",
    "반드시 오른다",
    "매수 신호",
    "매도 신호",
    "안전하다",
]

DISCLAIMER = "이 글은 투자 권유가 아니라 주식 용어와 기업분석 방법을 설명하기 위한 교육 콘텐츠입니다."


def validate_file(filepath: Path, content_root: Path) -> tuple[list[str], list[str]]:
    """Validate a single markdown article. Returns (errors, warnings)."""
    errors = []
    warnings = []
    text = filepath.read_text(encoding="utf-8")

    # Parse frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not fm_match:
        errors.append("Missing frontmatter")
        return errors, warnings

    try:
        fm = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML frontmatter: {e}")
        return errors, warnings

    if not isinstance(fm, dict):
        errors.append("Frontmatter is not a dict")
        return errors, warnings

    # Determine content type
    content_type = fm.get("content_type", "concept")

    # Check required fields
    required = COMMON_REQUIRED_FIELDS[:]
    if content_type == "data-practice":
        required.extend(DATA_PRACTICE_EXTRA_FIELDS)

    for field in required:
        if field not in fm:
            errors.append(f"Missing field: {field}")

    # Validate field values
    if fm.get("topic") and fm["topic"] not in VALID_TOPICS:
        errors.append(f"Invalid topic: {fm['topic']}")
    if fm.get("status") and fm["status"] not in VALID_STATUSES:
        errors.append(f"Invalid status: {fm['status']}")
    if fm.get("difficulty") and fm["difficulty"] not in VALID_DIFFICULTIES:
        errors.append(f"Invalid difficulty: {fm['difficulty']}")
    if fm.get("content_type") and fm["content_type"] not in VALID_CONTENT_TYPES:
        errors.append(f"Invalid content_type: {fm['content_type']}")
    if fm.get("source_policy") and fm["source_policy"] not in VALID_SOURCE_POLICIES:
        errors.append(f"Invalid source_policy: {fm['source_policy']}")
    if fm.get("language") != "ko":
        errors.append(f"Language should be 'ko', got: {fm.get('language')}")
    if fm.get("tags") and len(fm["tags"]) != 5:
        errors.append(f"Expected 5 tags, got {len(fm['tags'])}")
    if fm.get("level") and not (1 <= fm["level"] <= 10):
        errors.append(f"Level out of range: {fm['level']}")
    if fm.get("description") and len(fm["description"]) > 120:
        warnings.append(f"Description too long: {len(fm['description'])} chars (max 120)")

    # Check required sections
    body = text[fm_match.end():]
    sections = CONCEPT_SECTIONS if content_type == "concept" else DATA_PRACTICE_SECTIONS
    for section in sections:
        if f"## {section}" not in body:
            errors.append(f"Missing section: ## {section}")

    # Check disclaimer
    if DISCLAIMER not in body:
        errors.append("Missing disclaimer footer")

    # Check Tags footer
    if not re.search(r"^Tags:", body, re.MULTILINE):
        errors.append("Missing 'Tags:' footer line")

    # Check for code block (diagram for concept, code for data-practice)
    if "```" not in body:
        if content_type == "concept":
            errors.append("No code block found (expected ASCII diagram)")
        else:
            errors.append("No code block found (expected Python code)")

    # Check for table
    if "|---" not in body and "| ---" not in body:
        errors.append("No markdown table found")

    # Check internal links (dead link detection)
    link_pattern = re.compile(r"\[.*?\]\((\./.*?\.md|\.\./.+?\.md)\)")
    for match in link_pattern.finditer(body):
        link_path = match.group(1)
        resolved = (filepath.parent / link_path).resolve()
        if not resolved.exists():
            warnings.append(f"Dead link: {link_path}")

    # Check forbidden expressions
    for expr in FORBIDDEN_EXPRESSIONS:
        if expr in body:
            warnings.append(f"Forbidden expression found: \"{expr}\"")

    return errors, warnings


def main():
    content_root = Path(__file__).parent.parent / "content" / "stock-terms" / "ko"
    strict = "--strict" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if args:
        files = [Path(f) for f in args]
    else:
        files = sorted(content_root.rglob("*.md"))

    total_errors = 0
    total_warnings = 0
    files_with_errors = 0

    for f in files:
        if f.name == ".gitkeep":
            continue
        errs, warns = validate_file(f, content_root)
        if strict:
            errs.extend(warns)
            warns = []
        if errs:
            files_with_errors += 1
            total_errors += len(errs)
            print(f"\n❌ {f.relative_to(content_root.parent.parent.parent)}")
            for e in errs:
                print(f"   • {e}")
        if warns:
            total_warnings += len(warns)
            if not errs:
                print(f"\n⚠️  {f.relative_to(content_root.parent.parent.parent)}")
            for w in warns:
                print(f"   ⚠ {w}")

    total_files = len([f for f in files if f.name != ".gitkeep"])
    print(f"\n{'=' * 50}")
    print(f"Validated: {total_files} files")
    print(f"Errors: {total_errors} in {files_with_errors} files")
    print(f"Warnings: {total_warnings}")
    print(f"Clean: {total_files - files_with_errors} files")

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
