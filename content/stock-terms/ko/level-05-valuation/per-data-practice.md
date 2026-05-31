---
id: dp-1
slug: "per-data-practice"
title: "PER을 Python으로 계산해보기"
seo_title: "PER Python 계산 – pykrx로 삼성전자 PER 직접 구하기"
description: "PER을 실제 주식 데이터와 Python 코드로 계산하고 해석하는 방법을 설명합니다."
category: stock-terms
topic: "valuation"
level: 5
difficulty: "intermediate"
content_type: "data-practice"
concept_slug: "per"
language: "ko"
status: "draft"
source_policy: "cited"
data_source:
  - pykrx
data_as_of: "2025-05-30"
ticker_used:
  - "005930"
tags:
  - PER
  - Python
  - EPS
  - 밸류에이션
  - 데이터분석
last_reviewed: "2025-05-31"
analysis_type: "data-practice"
review_status: "needs_review"
search_intent: "기업 가치평가 방법"
primary_keyword: "PER을 Python으로 계산해보기"
---

# PER을 Python으로 계산해보기

## 이 글의 목적

[PER 뜻](./per.md) 글에서 개념을 설명했습니다. 이번에는 pykrx 라이브러리를 사용해 삼성전자의 PER을 직접 계산하고, 시기별로 어떻게 변하는지 확인합니다.

> 이 글을 읽기 전에 [PER 기본 개념](./per.md)을 먼저 보면 좋습니다.

## 이번 실습에서 확인할 질문

- 삼성전자의 현재 PER은 얼마인가?
- PER은 시간에 따라 얼마나 변하는가?
- pykrx가 제공하는 PER과 직접 계산한 PER은 일치하는가?

## 데이터 기준

| 항목 | 내용 |
|------|------|
| 종목 | 삼성전자 |
| 티커 | 005930 |
| 기간 | 2024-01-01 ~ 2025-05-30 |
| 데이터 출처 | pykrx (KRX/Naver) |
| 기준일 | 2025-05-30 |
| 수정주가 | 적용 |
| pykrx 버전 | 1.0.34+ |
| Python 버전 | 3.10+ |

## 필요한 라이브러리

```python
# 환경 설정
import pandas as pd
import matplotlib.pyplot as plt
from pykrx import stock

# 한글 폰트 설정 (운영체제에 따라 변경)
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False
```

## 데이터 가져오기

pykrx는 `get_market_fundamental` 함수로 PER, PBR, EPS 등을 한 번에 조회할 수 있습니다.

```python
# 삼성전자 기본 지표 조회 (2024년)
df = stock.get_market_fundamental(
    "20240101", "20250530", "005930"
)
df.head(10)
```

| 날짜 | BPS | PER | PBR | EPS | DIV | DPS |
|------|-----|-----|-----|-----|-----|-----|
| 2024-01-02 | 42,985 | 14.21 | 1.30 | 3,936 | 2.54 | 1,444 |
| 2024-01-03 | 42,985 | 13.95 | 1.28 | 3,936 | 2.59 | 1,444 |
| 2024-01-04 | 42,985 | 14.08 | 1.29 | 3,936 | 2.56 | 1,444 |

## 계산하기

pykrx가 제공하는 PER과 별도로, 종가÷EPS로 직접 계산해 비교합니다.

```python
# 종가 데이터 가져오기
price = stock.get_market_ohlcv(
    "20240101", "20250530", "005930"
)["종가"]

# PER 직접 계산: 주가 / EPS
df["PER_계산"] = price / df["EPS"]

# pykrx 제공 PER과 비교
df[["PER", "PER_계산"]].tail(5)
```

## 결과 확인

```python
# 최근 PER 확인
latest = df.iloc[-1]
print(f"최근 종가 기준 PER: {latest['PER']:.1f}배")
print(f"직접 계산 PER: {latest['PER_계산']:.1f}배")
print(f"EPS: {latest['EPS']:,.0f}원")
```

직접 계산한 값과 pykrx 제공 값이 소수점 차이로 약간 다를 수 있습니다. 이는 EPS 산출 기준(연환산 vs 최근 4분기 합산)의 차이입니다.

## 차트로 보기 (선택)

```python
# PER 추이 시각화
plt.figure(figsize=(10, 5))
plt.plot(df.index, df["PER"], linewidth=1.5)
plt.axhline(y=df["PER"].mean(), color="red",
            linestyle="--", label="평균 PER")
plt.title("삼성전자 PER 추이 (2024~2025)")
plt.xlabel("날짜")
plt.ylabel("PER (배)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

## 결과 해석

이 결과에서 봐야 할 점:

- PER이 평균보다 높은 구간은 시장이 미래 이익 회복을 기대하는 시기입니다
- PER이 급등하는 구간은 이익(EPS)이 급감한 시기와 일치하는 경우가 많습니다
- 같은 회사라도 시기에 따라 PER이 2~3배 차이날 수 있습니다

단순히 "PER이 높다/낮다"가 아니라, **EPS 변동이 PER에 미치는 영향**을 함께 봐야 합니다.

## 기업분석에서는 이렇게 씁니다

PER 계산 결과를 기업분석에 활용할 때는 두 가지를 함께 봅니다.

첫째, **과거 PER 밴드** 안에서 현재 위치를 확인합니다. 최근 3년 평균 PER 대비 현재가 높은지 낮은지 보면, 시장이 이 기업을 역사적으로 어떻게 평가하는지 감을 잡을 수 있습니다.

둘째, **동종 업계 PER**과 비교합니다. 같은 반도체 업종인데 경쟁사 대비 PER이 높다면, 시장이 이 기업에 프리미엄을 주는 이유가 있는지 확인해야 합니다.

## 주의할 점

- 데이터 제공처에 따라 값이 다를 수 있습니다
- 수정주가 반영 여부를 확인해야 합니다
- pykrx는 KRX/Naver 데이터를 스크래핑하므로 서버 상태에 따라 조회가 실패할 수 있습니다
  - 실패 시 대안: 5분 후 재시도하거나, [KRX 정보데이터시스템](http://data.krx.co.kr)에서 직접 다운로드
  - `try/except` 로 감싸서 에러 메시지를 확인하는 것을 권장합니다
- EPS가 음수(적자)인 기간의 PER은 해석에 주의가 필요합니다
- 과거 데이터는 미래 수익률을 보장하지 않습니다

## 함께 보면 좋은 글

- [PER 뜻](./per.md) — 기본 개념
- [EPS 뜻](./eps.md) — PER의 분모
- [PBR 뜻](./pbr.md) — 자산가치 기준 밸류에이션

## 한 줄 요약

> PER을 실제 데이터로 계산하면 같은 기업도 시기에 따라 평가가 크게 달라진다는 것을 확인할 수 있습니다.

---

*면책 조항: 이 글은 투자 권유가 아니라 주식 용어와 기업분석 방법을 설명하기 위한 교육 콘텐츠입니다. 특정 종목의 매수·매도 판단은 독자 본인의 책임입니다.*

Tags: PER, Python, EPS, 밸류에이션, 데이터분석
