# PRD: Stock Visual Note

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| 프로젝트명 | Stock Visual Note (주식이 보이는 노트) |
| 목표 | 주식 초보가 용어를 이해하고, 그 용어로 실제 기업을 분석할 수 있게 만드는 한국어 투자 학습 콘텐츠 |
| 채널 | Tistory 블로그 (stockvisualnote.tistory.com) |
| 대상 독자 | 주식 입문자~초중급 (투자 경험 0~2년) |
| 언어 | 한국어 |
| 콘텐츠 형태 | 마크다운 기반 정형 구조 글 |

## 핵심 가치

1. **쉬움** — 초등학생도 첫 문장은 이해할 수 있어야 한다
2. **시각화** — 모든 글에 Mermaid 다이어그램 + 표가 필수
3. **연결** — 용어 하나가 기업분석까지 이어지는 학습 경로
4. **중립** — 투자 권유 없음. 교육 목적만.

## 콘텐츠 모델

### 글 유형

| 유형 | 설명 | 템플릿 |
|------|------|--------|
| 용어 설명 | 주식 용어 하나를 12섹션으로 설명 | `templates/term-post-template.md` |
| 기업분석 | 실제 기업을 프레임워크로 분석 (향후) | `templates/company-analysis-template.md` |

### 메타데이터 스키마 (Frontmatter)

#### 공통 필드 (모든 글 필수)

```yaml
id: number            # 글 번호 (1~500)
slug: string          # URL용 영문 식별자
title: string         # 글 제목
seo_title: string     # 검색 최적화 제목
description: string   # SEO 메타 설명 (120자 이내)
category: string      # stock-terms | company-analysis
topic: string         # 주제 분류 (basic, market-trading, financial-statements, ratios, valuation, events, earnings, industry-macro, strategy-risk, company-analysis)
level: number         # 난이도 레벨 (1~10)
difficulty: string    # beginner | intermediate | advanced
content_type: string  # concept | data-practice
language: "ko"
status: string        # draft | review | published
source_policy: string # hypothetical | cited
search_intent: string # 사용자 검색 의도 (예: "PER 뜻", "주식 PER이란")
primary_keyword: string # 핵심 키워드 (seo_title에 반드시 포함)
tags: string[]        # 5개 태그 (한국어)
last_reviewed: date   # 마지막 검토일
```

#### 데이터 실습형 추가 필드 (content_type: data-practice)

```yaml
concept_slug: string  # 연결할 기본 설명형 글의 slug (예: per)
data_source: string[] # 사용 라이브러리 (예: [pykrx])
data_as_of: date      # 데이터 기준일 (예: 2026-05-31)
ticker_used: string[] # 예시 종목 티커 (예: ["005930"])
```

### 12섹션 구조 (용어 글)

| # | 섹션 | 목적 |
|---|------|------|
| 1 | 한 줄 정의 | 사전적 정의 |
| 2 | 아주 쉽게 말하면 | 비유·일상어 설명 |
| 3 | 왜 중요한가 | 투자에서의 의미 |
| 4 | 그림으로 이해하기 | Mermaid 다이어그램 |
| 5 | 숫자로 보는 예시 | 가상 기업 수치 |
| 6 | 표로 비교하기 | 개념 비교 테이블 |
| 7 | 초보자가 자주 하는 오해 | 2개 오해 + 해소 |
| 8 | 고수는 이렇게 봅니다 | 숙련자 관점 |
| 9 | 기업분석에서는 이렇게 씁니다 | 실전 활용법 |
| 10 | 함께 보면 좋은 용어 | 내부 링크 (상대 경로) |
| 11 | 정리 | 핵심 요약 |
| 12 | 한 줄 요약 | 인용구 형태 마무리 |

### 필수 푸터

```
*면책 조항: 이 글은 투자 권유가 아니라 주식 용어와 기업분석 방법을 설명하기 위한 교육 콘텐츠입니다. 특정 종목의 매수·매도 판단은 독자 본인의 책임입니다.*

Tags: tag1, tag2, tag3, tag4, tag5
```

## 레벨 체계

| Level | 폴더명 | 주제 | topic 값 |
|-------|--------|------|-----------|
| 1 | level-01-basic | 주식 기본 언어 | basic |
| 2 | level-02-market-trading | 시장과 거래 | market-trading |
| 3 | level-03-financial-statements | 재무제표 기초 | financial-statements |
| 4 | level-04-ratios | 수익성·안정성 지표 | ratios |
| 5 | level-05-valuation | 밸류에이션 | valuation |
| 6 | level-06-events | 배당과 주주환원 | events |
| 7 | level-07-earnings | 공시·자본 이벤트 | earnings |
| 8 | level-08-industry-macro | 실적·컨센서스 | industry-macro |
| 9 | level-09-strategy-risk | 산업·매크로 | strategy-risk |
| 10 | level-10-company-analysis | 투자전략·기업분석 연결 | company-analysis |

> **참고**: Level 7-9의 영문 폴더명(earnings, industry-macro, strategy-risk)은 초기 설계 시 정해진 식별자입니다. 실제 콘텐츠 주제는 한국어 설명을 따릅니다. 폴더명 변경 시 100개 글의 상호 링크가 깨지므로 현행 유지합니다.

## 금지 표현

다음 표현은 어떤 글에서도 사용하지 않습니다:

- "이 종목은 지금 사야 합니다"
- "목표가는 얼마입니다"
- "무조건 장기 보유하면 됩니다"
- "이 지표가 낮으면 무조건 저평가입니다"
- "손해 볼 가능성이 낮습니다"
- "확정 수익이 가능합니다"

## 로드맵

| 마일스톤 | 글 수 | 내용 |
|----------|-------|------|
| MVP (완료) | 100개 | 레벨 1~10, 핵심 용어 커버 |
| 2차 | 200개 | 레벨별 확장 (심화 용어) |
| 3차 | 300개 | 비교 글, 조합 글 추가 |
| 4차 | 400~500개 | 기업분석 실전 글 추가 |

## 배포 채널

| 채널 | 상태 | 용도 |
|------|------|------|
| Tistory | 활성 | 1차 발행 |
| GitHub | 활성 | 원본 저장소 |
| 전자책 | 계획 | 레벨별 묶음 |
| 뉴스레터 | 계획 | 주간 용어 발행 |

## 성공 지표

- 월간 검색 유입 1,000명 (6개월 내)
- 글당 평균 체류시간 3분 이상
- 100개 글 기준 상호 링크 커버율 80% 이상

## Python 기반 실제 데이터 설명 전략

본 블로그는 단순한 용어 설명에 그치지 않고, 일부 핵심 개념은 Python 코드와 실제 주식 데이터를 활용해 설명한다.

### 목적

- 용어와 지표가 실제 데이터에서 어떻게 계산되는지 보여준다
- 초보자가 숫자를 직접 확인하며 개념을 이해하도록 돕는다
- 기업분석 콘텐츠로 확장할 때 재현 가능한 분석 흐름을 만든다
- 단순 주장보다 데이터 기반 해석을 강화한다

### 글 유형 분리

| 유형 | 목적 | 대상 독자 | Python 코드 |
|------|------|-----------|-------------|
| 기본 설명형 | 개념 이해 | 초보자 | 없음 |
| 데이터 실습형 | 실제 데이터로 검증 | 중급 이상 | 포함 |

같은 용어라도 두 글로 분리할 수 있다:

```
PER 뜻, 주식 초보가 반드시 알아야 하는 이유       → 기본 설명형
PER을 Python으로 계산해보기, 삼성전자 데이터 예시  → 데이터 실습형
```

### 적용 우선순위

| 콘텐츠 | Python 코드 |
|--------|-------------|
| 주식 뜻, 주가 뜻, 시가총액 뜻 | 선택 |
| 거래량, 등락률, 변동성 | 권장 |
| PER, PBR, ROE, EPS | 권장 |
| 영업이익률, 순이익률, 부채비율 | 권장 |
| 유상증자, 감자, 배당락 | 선택 |
| 실적 발표 전후 주가 변화 | 강력 권장 |
| 기업분석 글 | 강력 권장 |

### 데이터 실습형 메타데이터

기본 설명형과 구분하기 위해 frontmatter에 아래 필드를 추가한다 (위 "데이터 실습형 추가 필드" 참조):

```yaml
content_type: "data-practice"
concept_slug: "per"            # 연결할 개념 글 slug
data_source:
  - pykrx
data_as_of: "2026-05-31"
ticker_used:
  - "005930"
```

기본 설명형 글은 `content_type: "concept"`으로 설정한다.

### 데이터 라이브러리

| 라이브러리 | 용도 | 비고 |
|-----------|------|------|
| pykrx | 한국 주식 (KRX/Naver) | 1순위 |
| yfinance | 해외 주식 (Yahoo Finance) | 해외 확장 시 |
| FinanceDataReader | 국내외 통합 | 보조 |

### 데이터 사용 원칙

- 데이터 출처를 명시한다
- 기준일을 명시한다
- 코드가 실행 가능하도록 작성한다
- 과도한 API 호출을 피한다
- 데이터 제공처의 약관을 준수한다
- 결과를 투자 권유처럼 해석하지 않는다
- 수정주가 반영 여부를 확인해야 한다
- 과거 데이터는 미래 수익률을 보장하지 않는다
