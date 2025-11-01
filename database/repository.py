from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from .models import StockAnalysisCache, StockSymbolMapping
from models import StockResponse, RecommendationDetail


class StockRepository:
    """주식 데이터 접근 계층"""

    def __init__(self, db: Session):
        self.db = db

    # ============================================================
    # 심볼 매핑 캐시
    # ============================================================

    def get_symbol_mapping(self, input_query: str) -> Optional[Tuple[str, str]]:
        """
        입력 쿼리로 심볼 매핑 조회

        Args:
            input_query: 사용자 입력 (예: "테슬라", "TSLA")

        Returns:
            (심볼, 기업명) 튜플 또는 None
        """
        mapping = (
            self.db.query(StockSymbolMapping)
            .filter(StockSymbolMapping.input_query == input_query.strip())
            .first()
        )

        if mapping:
            return (mapping.symbol, mapping.company_name)
        return None

    def save_symbol_mapping(self, input_query: str, symbol: str, company_name: str):
        """
        심볼 매핑 저장 (upsert)

        Args:
            input_query: 사용자 입력
            symbol: 주식 심볼
            company_name: 정식 기업명
        """
        existing = (
            self.db.query(StockSymbolMapping)
            .filter(StockSymbolMapping.input_query == input_query.strip())
            .first()
        )

        if existing:
            # 업데이트
            existing.symbol = symbol
            existing.company_name = company_name
            existing.updated_at = datetime.utcnow()
        else:
            # 생성
            mapping = StockSymbolMapping(
                input_query=input_query.strip(),
                symbol=symbol,
                company_name=company_name,
            )
            self.db.add(mapping)

        self.db.commit()

    # ============================================================
    # 주식 분석 캐시
    # ============================================================

    def get_cached_analysis(
        self, symbol: str, max_age_hours: int = 24
    ) -> Optional[StockResponse]:
        """
        캐시된 주식 분석 조회 (최신 데이터만)

        Args:
            symbol: 주식 심볼
            max_age_hours: 캐시 유효 시간 (기본 24시간)

        Returns:
            StockResponse 또는 None
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)

        cache = (
            self.db.query(StockAnalysisCache)
            .filter(StockAnalysisCache.symbol == symbol)
            .filter(StockAnalysisCache.updated_at >= cutoff_time)
            .order_by(desc(StockAnalysisCache.updated_at))
            .first()
        )

        if cache:
            return StockResponse(
                symbol=cache.symbol,
                company_name=cache.company_name,
                short_term=RecommendationDetail(
                    action=cache.short_term_action, reason=cache.short_term_reason
                ),
                mid_term=RecommendationDetail(
                    action=cache.mid_term_action, reason=cache.mid_term_reason
                ),
                long_term=RecommendationDetail(
                    action=cache.long_term_action, reason=cache.long_term_reason
                ),
                analysis=cache.analysis,
            )

        return None

    def save_analysis(self, response: StockResponse):
        """
        주식 분석 결과 저장

        Args:
            response: StockResponse 객체
        """
        cache = StockAnalysisCache(
            symbol=response.symbol,
            company_name=response.company_name,
            short_term_action=response.short_term.action,
            short_term_reason=response.short_term.reason,
            mid_term_action=response.mid_term.action,
            mid_term_reason=response.mid_term.reason,
            long_term_action=response.long_term.action,
            long_term_reason=response.long_term.reason,
            analysis=response.analysis,
        )

        self.db.add(cache)
        self.db.commit()

    def delete_old_cache(self, days: int = 30):
        """
        오래된 캐시 데이터 삭제

        Args:
            days: 삭제 기준 일수 (기본 30일)
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days)

        self.db.query(StockAnalysisCache).filter(
            StockAnalysisCache.updated_at < cutoff_time
        ).delete()

        self.db.commit()
