from fastapi import APIRouter, HTTPException
from models import StockResponse
from services import StockService

router = APIRouter(prefix="/api/stock", tags=["stock"])

# 서비스 인스턴스 생성
stock_service = StockService()


@router.get("/{company}", response_model=StockResponse)
async def get_stock_analysis(company: str):
    """
    주식 종목을 종합 분석하고 매수/매도/홀딩 추천을 제공하는 API
    기업명 또는 심볼 모두 사용 가능 (예: "테슬라", "TSLA", "엔비디아", "NVDA")

    Args:
        company: 기업명 또는 심볼

    Returns:
        StockResponse: 분석 결과
    """
    try:
        return stock_service.analyze_stock(company)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
