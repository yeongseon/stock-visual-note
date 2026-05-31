# 발행 워크플로우 (Publishing Workflow)

## 개요

콘텐츠 작성 → 검증 → 발행까지의 전체 과정을 정의합니다.

## 1단계: 콘텐츠 작성

1. `templates/term-post-template.md` 또는 `templates/data-practice-template.md`를 복사
2. 적절한 `content/stock-terms/ko/level-XX-*/` 디렉토리에 저장
3. frontmatter 모든 필드 채우기 (status: "draft")
4. 12개 섹션 모두 작성
5. `content-catalog.yaml`에 항목 추가

## 2단계: 자체 검증

```bash
# 단일 파일 검증
python3 scripts/validate.py content/stock-terms/ko/level-01-basic/stock.md

# 전체 검증 (strict)
python3 scripts/validate.py --strict
```

### 체크리스트

- [ ] validate.py 통과 (0 errors, 0 warnings)
- [ ] [품질 체크리스트](./quality-checklist.md) 수동 확인
- [ ] 내부 링크 클릭 테스트
- [ ] 숫자 예시에 "가상 예시" 표시 확인

## 3단계: 리뷰

1. PR 생성 (GitHub Actions CI 자동 실행)
2. frontmatter `status`를 `"review"`로 변경
3. 리뷰어 검토 후 승인

## 4단계: 발행

1. `status`를 `"published"`로 변경
2. `review_status`를 `"approved"`로 변경
3. `last_reviewed`를 오늘 날짜로 업데이트
4. Tistory 빌드 실행:

```bash
python3 scripts/build_tistory.py content/stock-terms/ko/level-01-basic/stock.md
```

5. 빌드 결과물을 Tistory 에디터에 붙여넣기 (HTML 모드)

## 5단계: 발행 후

- 검색 콘솔에서 인덱싱 요청
- 내부 링크 대상이 된 다른 글에서 링크 연결 확인
- 1주 후 검색 노출 확인 → `last_reviewed` 업데이트

## 상태 흐름도

```
draft → review → published
  ↑                    │
  └────── (수정 필요) ──┘
```

## Frontmatter 상태 필드 정리

| 필드 | 값 | 의미 |
|------|-----|------|
| status | draft | 작성 중 |
| status | review | 리뷰 대기 |
| status | published | 발행 완료 |
| review_status | needs_review | 리뷰 필요 |
| review_status | reviewed | 리뷰 완료 |
| review_status | approved | 최종 승인 |
