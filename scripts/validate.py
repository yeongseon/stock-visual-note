#!/usr/bin/env python3
"""
Frontmatter validator for stock-visual-note articles.
Checks required fields, section headings, link validity, forbidden expressions,
H1/title alignment, footer/frontmatter tag sync, and catalog sync.

Usage:
    python3 scripts/validate.py                    # validate all articles
    python3 scripts/validate.py content/.../per.md # validate specific file
    python3 scripts/validate.py --strict           # treat warnings as errors
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
    "category",
    "topic",
    "level",
    "difficulty",
    "content_type",
    "language",
    "status",
    "source_policy",
    "tags",
    "last_reviewed",
    "analysis_type",
    "review_status",
    "search_intent",
    "primary_keyword",
]

DATA_PRACTICE_EXTRA_FIELDS = [
    "concept_slug",
    "data_source",
    "data_as_of",
    "ticker_used",
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
VALID_CATEGORIES = ["stock-terms", "company-analysis"]
VALID_SOURCE_POLICIES = ["hypothetical", "cited"]
VALID_ANALYSIS_TYPES = ["concept", "data-practice"]
VALID_REVIEW_STATUSES = ["needs_review", "reviewed", "approved"]

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
    "지금이 매수 기회",
    "저평가가 확실",
    "고평가가 확실",
    "반드시 매수",
    "반드시 매도",
    "수익이 보장",
    "원금 보장",
]

DISCLAIMER = "이 글은 투자 권유가 아니라 주식 용어와 기업분석 방법을 설명하기 위한 교육 콘텐츠입니다. 특정 종목의 매수·매도 판단은 독자 본인의 책임입니다."


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
    if fm.get("category") and fm["category"] not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {fm['category']}")
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
    if fm.get("analysis_type") and fm["analysis_type"] not in VALID_ANALYSIS_TYPES:
        errors.append(f"Invalid analysis_type: {fm['analysis_type']}")
    if fm.get("review_status") and fm["review_status"] not in VALID_REVIEW_STATUSES:
        errors.append(f"Invalid review_status: {fm['review_status']}")
    if fm.get("tags") and len(fm["tags"]) != 5:
        errors.append(f"Expected exactly 5 tags, got {len(fm['tags'])}")
    if fm.get("level") and not (1 <= fm["level"] <= 10):
        errors.append(f"Level out of range: {fm['level']}")
    if fm.get("description") and len(fm["description"]) > 120:
        warnings.append(
            f"Description too long: {len(fm['description'])} chars (max 120)"
        )

    # --- Body checks ---
    body = text[fm_match.end() :]

    # Check required sections (in order)
    sections = CONCEPT_SECTIONS if content_type == "concept" else DATA_PRACTICE_SECTIONS
    section_positions = []
    for section in sections:
        pos = body.find(f"## {section}")
        if pos == -1:
            errors.append(f"Missing section: ## {section}")
        else:
            section_positions.append(pos)

    # Check section order
    if len(section_positions) >= 2:
        for i in range(len(section_positions) - 1):
            if section_positions[i] >= section_positions[i + 1]:
                errors.append("Sections are out of order")
                break

    # Check H1 matches title
    h1_match = re.search(r"^# (.+)$", body, re.MULTILINE)
    if h1_match:
        h1 = h1_match.group(1).strip()
        title = fm.get("title", "")
        # H1 should contain the core of the title (allow H1 to have extra suffix like " — ...")
        if title and h1 != title:
            # Allow H1 to be title with additional descriptor
            if not h1.startswith(title.split(",")[0].split("—")[0].strip()):
                warnings.append(
                    f"H1/title mismatch: H1='{h1[:40]}' vs title='{title[:40]}'"
                )

    # Check disclaimer
    if DISCLAIMER not in body:
        errors.append("Missing disclaimer footer")

    # Check Tags footer
    tags_match = re.search(r"^Tags:\s*(.+)$", body, re.MULTILINE)
    if not tags_match:
        errors.append("Missing 'Tags:' footer line")
    else:
        # Check footer tags match frontmatter tags
        footer_tags_str = tags_match.group(1).strip()
        footer_tags = [t.strip() for t in footer_tags_str.split(",")]
        fm_tags = fm.get("tags", [])
        if fm_tags and set(footer_tags) != set(fm_tags):
            warnings.append(
                f"Footer/frontmatter tag mismatch: footer={len(footer_tags)} vs fm={len(fm_tags)}"
            )

    # Check for code block (diagram for concept, code for data-practice)
    if "```" not in body:
        if content_type == "concept":
            errors.append("No code block found (expected diagram)")
        else:
            errors.append("No code block found (expected Python code)")

    # Check code fence parity (odd count means broken formatting)
    fence_count = body.count('```')
    if fence_count % 2 != 0:
        errors.append(f"Odd number of code fences ({fence_count}): broken formatting")
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

    # Check forbidden expressions (skip quoted/negation context)
    for expr in FORBIDDEN_EXPRESSIONS:
        for line in body.split("\n"):
            if expr in line:
                stripped = line.strip()
                if (
                    stripped.startswith('"')
                    or '**"' in stripped
                    or stripped.startswith("> ❌")
                    or stripped.startswith("❌")
                    or "아닙니다" in line
                    or "아니다" in line
                    or "오해" in line
                    or "착각" in line
                    or "산정" in line
                    or "공식" in line
                    or "리포트" in line
                    or "하향" in line
                    or "상향" in line
                    or "추정" in line
                    or "타겟" in line
                    or "표현" in line
                    or "= " in line
                    or "뜻" in line
                    or "의미" in line
                    or "│" in line
                    or "분석" in line
                    or "계산" in line
                    or "공시" in line
                    or "비교" in line
                    or "철회" in line
                    or "vs" in line
                ):
                    continue
                warnings.append(
                    f'Forbidden expression found: "{expr}" in: {stripped[:50]}'
                )
                break

    # Check primary_keyword appears in seo_title
    pk = fm.get("primary_keyword", "")
    seo_title = fm.get("seo_title", "")
    if pk and seo_title and pk not in seo_title:
        warnings.append(f"primary_keyword '{pk}' not in seo_title")

    return errors, warnings


def validate_catalog_sync(content_root: Path) -> list[str]:
    """Check that content-catalog.yaml and article files are in sync."""
    errors = []
    catalog_path = content_root.parent.parent.parent / "content-catalog.yaml"
    if not catalog_path.exists():
        errors.append("content-catalog.yaml not found")
        return errors

    catalog = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
    # Extract all slugs from catalog
    catalog_slugs = set()
    if isinstance(catalog, dict):
        for section in catalog.values():
            if isinstance(section, list):
                for item in section:
                    if isinstance(item, dict) and "slug" in item:
                        catalog_slugs.add(item["slug"])

    # Get all article slugs from files
    file_slugs = set()
    for f in content_root.rglob("*.md"):
        if f.name == ".gitkeep":
            continue
        text = f.read_text(encoding="utf-8")
        fm_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
        if fm_match:
            try:
                fm = yaml.safe_load(fm_match.group(1))
                if isinstance(fm, dict) and "slug" in fm:
                    file_slugs.add(fm["slug"])
            except yaml.YAMLError:
                pass

    missing_from_catalog = file_slugs - catalog_slugs
    for slug in sorted(missing_from_catalog):
        errors.append(f"Article '{slug}' not in content-catalog.yaml")

    return errors


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__.strip())
        return 0

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

    # Catalog sync check (only when validating all files)
    if not args:
        catalog_errors = validate_catalog_sync(content_root)
        for e in catalog_errors:
            total_errors += 1
            print(f"\n❌ [catalog] {e}")
        if catalog_errors:
            files_with_errors += 1

    total_files = len([f for f in files if f.name != ".gitkeep"])
    print(f"\n{'=' * 50}")
    print(f"Validated: {total_files} files")
    print(f"Errors: {total_errors} in {files_with_errors} files")
    print(f"Warnings: {total_warnings}")
    print(f"Clean: {total_files - files_with_errors} files")

    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
