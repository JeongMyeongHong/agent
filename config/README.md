# 검색 소스 설정 가이드

## 개요

이 설정은 AI가 주식 정보를 검색할 때 **어떤 웹사이트에서만** 정보를 가져올지 제한합니다.

## 파일 구조

```
config/
├── __init__.py
├── search_sources.py  # 검색 소스 설정
└── README.md         # 이 문서
```

## 검색 소스 관리

### 현재 설정된 소스

**미국 주식:**
- Bloomberg (bloomberg.com)
- Reuters (reuters.com)
- CNBC (cnbc.com)
- MarketWatch (marketwatch.com)
- Yahoo Finance (yahoo.com/finance)
- SEC (sec.gov)
- Investing.com (investing.com)
- The Motley Fool (fool.com)
- Seeking Alpha (seekingalpha.com)

**한국 주식:**
- 네이버 금융 (naver.com/finance)
- 전자공시시스템 (dart.fss.or.kr)
- 한국경제 (hankyung.com)
- 매일경제 (mk.co.kr)
- 서울경제 (sedaily.com)
- 연합인포맥스 (news.einfomax.co.kr)

## 소스 추가/제거 방법

### 1. 소스 추가

`config/search_sources.py` 파일 수정:

```python
# 미국 주식 소스에 추가
US_STOCK_SOURCES = [
    "bloomberg.com",
    "reuters.com",
    # ... 기존 소스들
    "your-new-source.com",  # 새 소스 추가
]

# 한국 주식 소스에 추가
KR_STOCK_SOURCES = [
    "naver.com/finance",
    # ... 기존 소스들
    "새로운소스.com",  # 새 소스 추가
]
```

### 2. 소스 제거

해당 라인을 삭제하거나 주석 처리:

```python
US_STOCK_SOURCES = [
    "bloomberg.com",
    # "reuters.com",  # 주석 처리로 비활성화
]
```

### 3. 변경사항 적용

파일을 저장하면 **다음 요청부터 자동 적용**됩니다. 재시작 불필요!

## 동작 원리

### Brave Search의 site: 연산자

```
# 단일 사이트 검색
site:bloomberg.com TSLA stock news

# 결과: bloomberg.com에서만 "TSLA stock news" 검색
```

### AI의 검색 쿼리 예시

사용자가 "테슬라 분석해줘" 요청 시:

```python
# AI가 자동으로 생성하는 검색 쿼리들:
1. "site:bloomberg.com TSLA stock news latest"
2. "site:reuters.com Tesla earnings report"
3. "site:sec.gov Tesla 10-K filing"
```

## 보안 및 신뢰성

### 왜 특정 사이트만 허용하나요?

1. **정보 신뢰성**: 검증된 금융 뉴스 출처만 사용
2. **오정보 방지**: 부정확한 블로그/커뮤니티 제외
3. **법적 준수**: 공식 공시 자료 우선

### 권장 출처 기준

✅ **포함해야 할 사이트:**
- 공식 금융 뉴스 기관
- 정부 공식 공시 사이트
- 대형 증권정보 플랫폼

❌ **제외해야 할 사이트:**
- 개인 블로그
- 익명 커뮤니티 (레딧, 디시인사이드 등)
- 광고성 사이트

## 고급 설정

### 프로그래밍 방식으로 쿼리 생성

```python
from config import format_site_query, US_STOCK_SOURCES

# 여러 사이트를 OR 조건으로 검색
query = format_site_query(
    sites=["bloomberg.com", "reuters.com"],
    query="TSLA stock"
)
# 결과: "(site:bloomberg.com OR site:reuters.com) TSLA stock"
```

### 특정 조건에 따라 소스 변경

```python
# 예: 한국 주식이면 한국 소스만 사용
from config import KR_STOCK_SOURCES, US_STOCK_SOURCES

def get_sources_for_market(symbol: str):
    if symbol.endswith('.KS') or symbol.endswith('.KQ'):
        return KR_STOCK_SOURCES
    else:
        return US_STOCK_SOURCES
```

## 트러블슈팅

### 검색 결과가 너무 적을 때

→ 더 많은 신뢰할 수 있는 소스를 추가하세요.

### 특정 사이트가 차단될 때

→ 해당 사이트가 Brave Search에서 인덱싱되는지 확인:
```bash
# 브라우저에서 직접 테스트
site:your-site.com stock news
```

### 검색이 너무 느릴 때

→ 소스 개수를 줄이거나, AI가 한 번에 검색하는 쿼리 수를 제한하세요.

## 예제

### 예제 1: 암호화폐 소스 추가

```python
# search_sources.py에 추가
CRYPTO_SOURCES = [
    "coindesk.com",
    "cointelegraph.com",
    "decrypt.co",
]

ALLOWED_SOURCES = US_STOCK_SOURCES + KR_STOCK_SOURCES + CRYPTO_SOURCES
```

### 예제 2: 특정 국가 시장 추가

```python
# 일본 주식
JP_STOCK_SOURCES = [
    "nikkei.com",
    "japantimes.co.jp/business",
]
```

## 참고 자료

- [Brave Search API 문서](https://brave.com/search/api/)
- [Google Search 연산자](https://support.google.com/websearch/answer/2466433)
