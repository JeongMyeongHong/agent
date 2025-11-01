from pydantic import BaseModel


class StockRequest(BaseModel):
    """주식 분석 요청 모델"""
    company: str  # 기업명 또는 심볼 (예: "테슬라", "TSLA", "엔비디아", "NVDA")


class RecommendationDetail(BaseModel):
    """투자 의견 상세"""
    action: str  # BUY, SELL, HOLD
    reason: str  # 해당 투자 의견의 이유


class StockResponse(BaseModel):
    """주식 분석 응답 모델"""
    symbol: str
    company_name: str  # 정식 기업명 (예: "Tesla, Inc.")
    short_term: RecommendationDetail  # 단기 (1일~1주일)
    mid_term: RecommendationDetail    # 중기 (1주일~3개월)
    long_term: RecommendationDetail   # 장기 (3개월~1년)
    analysis: str  # 종합 분석
