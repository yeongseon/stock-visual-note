# Stock Visual Note

**주식이 보이는 노트**는 주식 초보를 위해 어려운 투자 용어, 재무제표, 공시, 실적, 산업, 기업분석 개념을 그림과 표로 쉽게 정리하는 한국어 투자 학습 콘텐츠 저장소입니다.

## 한 줄 소개

> 용어를 외우는 데서 끝나지 않고, 기업을 읽는 힘까지 기르는 주식 공부 노트입니다.

## 구조

```
content/stock-terms/ko/
├── level-01-basic/                # 주식 기본 언어 (10개)
├── level-02-market-trading/       # 시장과 거래 (10개)
├── level-03-financial-statements/ # 재무제표 기초 (10개)
├── level-04-ratios/               # 수익성·안정성 지표 (10개)
├── level-05-valuation/            # 밸류에이션 (10개)
├── level-06-events/               # 배당과 주주환원 (10개)
├── level-07-earnings/             # 공시·자본 이벤트 (10개)
├── level-08-industry-macro/       # 실적·컨센서스 (10개)
├── level-09-strategy-risk/        # 산업·매크로 (10개)
└── level-10-company-analysis/     # 투자전략·기업분석 (10개)
```

현재 **101개 글 작성 완료** (개념 100 + 데이터 실습 1, Level 1~10, status: draft)

## 콘텐츠 로드맵

| 단계 | 글 수 | 상태 |
|------|-------|------|
| MVP | 100개 | ✅ 완료 |
| 2차 | 200개 | 📋 계획 |
| 3차 | 300개 | 📋 계획 |
| 최종 | 400~500개 | 📋 계획 |

## 콘텐츠 유형

| 유형 | 목적 | 대상 독자 | 현황 |
|------|------|-----------|------|
| 기본 설명형 (concept) | 용어 개념 이해 | 초보자 | 100개 완료 |
| 데이터 실습형 (data-practice) | Python + 실제 데이터로 검증 | 중급 이상 | 1개 완료 (PER) |

### 기본 설명형 (12 섹션)

모든 용어 글은 동일한 구조를 따릅니다:

1. 한 줄 정의
2. 아주 쉽게 말하면
3. 왜 중요한가
4. 그림으로 이해하기 (Mermaid 다이어그램)
5. 숫자로 보는 예시
6. 표로 비교하기
7. 초보자가 자주 하는 오해 (2개)
8. 고수는 이렇게 봅니다
9. 기업분석에서는 이렇게 씁니다
10. 함께 보면 좋은 용어
11. 정리
12. 한 줄 요약

### 데이터 실습형

Python 코드 + pykrx 데이터로 개념을 실제 주식 데이터에서 확인합니다. 기본 설명형 글과 1:1 연결됩니다.
## 채널

- 1차: [stockvisualnote.tistory.com](https://stockvisualnote.tistory.com)
- 확장: 전자책, 뉴스레터, 노션 템플릿

## 핵심 원칙

- 초보자도 이해할 수 있는 쉬운 설명
- 모든 글에 다이어그램과 표 포함
- 용어에서 시작해 기업분석으로 연결
- 투자 권유가 아닌 교육 목적 콘텐츠

## 발행 현황

| 레벨 | 글 수 | status | review_status |
|------|-------|--------|---------------|
| Level 1 (기본) | 10 | draft | needs_review |
| Level 2 (매매) | 10 | draft | needs_review |
| Level 3 (재무제표) | 10 | draft | needs_review |
| Level 4 (비율) | 10 | draft | needs_review |
| Level 5 (밸류에이션) | 11 | draft | needs_review |
| Level 6 (배당) | 10 | draft | needs_review |
| Level 7 (공시) | 10 | draft | needs_review |
| Level 8 (실적) | 10 | draft | needs_review |
| Level 9 (전략) | 10 | draft | needs_review |
| Level 10 (기업분석) | 10 | draft | needs_review |

## 학습 경로

순서대로 학습할 수 있는 코스를 제공합니다: [학습 경로 보기](./docs/learning-paths/README.md)

## 관련 문서

- [PRD.md](./PRD.md) — 프로젝트 정의서
- [STYLE_GUIDE.md](./STYLE_GUIDE.md) — 작성 스타일 가이드
- [DIAGRAM_GUIDE.md](./DIAGRAM_GUIDE.md) — 다이어그램 작성 가이드
- [content-catalog.yaml](./content-catalog.yaml) — 콘텐츠 카탈로그
- [docs/quality-checklist.md](./docs/quality-checklist.md) — 발행 전 품질 체크리스트
- [docs/publishing-workflow.md](./docs/publishing-workflow.md) — 발행 워크플로우
- [docs/learning-paths/](./docs/learning-paths/) — 학습 경로 가이드

## 기여 워크플로우

1. 이슈 또는 `content-catalog.yaml`에서 작성할 용어 선택
2. 템플릿 복사 → 작성 → `python3 scripts/validate.py --strict` 통과
3. PR 생성 → CI 통과 → 리뷰 → 머지

## 라이선스

이 저장소의 콘텐츠는 교육 목적으로 작성되었습니다. 무단 상업적 이용을 금합니다.
