"""
웹 검색 소스 설정

검색 허용 사이트를 관리합니다.
"""

# 미국 주식 정보 출처
US_STOCK_SOURCES = [
    "bloomberg.com",
    "reuters.com",
    "cnbc.com",
    "marketwatch.com",
    "yahoo.com/finance",
    "sec.gov",
    "investing.com",
    "fool.com",
    "seekingalpha.com",
]

# 한국 주식 정보 출처
KR_STOCK_SOURCES = [
    "naver.com/finance",
    "dart.fss.or.kr",
    "hankyung.com",
    "mk.co.kr",
    "sedaily.com",
    "news.einfomax.co.kr",
]

# 전체 허용 소스
ALLOWED_SOURCES = US_STOCK_SOURCES + KR_STOCK_SOURCES


def get_search_instruction() -> str:
    """검색 가이드라인 텍스트 생성"""
    us_sites = "\n".join([f"- site:{site}" for site in US_STOCK_SOURCES])
    kr_sites = "\n".join([f"- site:{site}" for site in KR_STOCK_SOURCES])

    return f"""**검색 시 반드시 다음 신뢰할 수 있는 사이트에서만 검색하세요:**

미국 주식:
{us_sites}

한국 주식:
{kr_sites}

검색 쿼리 예시:
- "site:bloomberg.com TSLA stock news"
- "site:reuters.com Tesla earnings"
- "site:naver.com/finance 삼성전자 주가"
"""


def format_site_query(sites: list[str], query: str) -> str:
    """
    여러 사이트를 OR 조건으로 검색 쿼리 생성

    예: format_site_query(["bloomberg.com", "reuters.com"], "TSLA")
    → "(site:bloomberg.com OR site:reuters.com) TSLA"
    """
    site_filters = " OR ".join([f"site:{site}" for site in sites])
    return f"({site_filters}) {query}"
