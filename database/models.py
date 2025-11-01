from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StockAnalysisCache(Base):
    """주식 분석 결과 캐시 테이블"""

    __tablename__ = "stock_analysis_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)  # 주식 심볼 (예: TSLA)
    company_name = Column(String(200), nullable=False)  # 정식 기업명

    # 분석 결과
    short_term_action = Column(String(10), nullable=False)  # BUY/SELL/HOLD
    short_term_reason = Column(Text, nullable=False)

    mid_term_action = Column(String(10), nullable=False)
    mid_term_reason = Column(Text, nullable=False)

    long_term_action = Column(String(10), nullable=False)
    long_term_reason = Column(Text, nullable=False)

    analysis = Column(Text, nullable=False)  # 종합 분석

    # 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # 복합 인덱스: 심볼 + 최신순 조회 최적화
    __table_args__ = (
        Index('idx_symbol_updated', 'symbol', 'updated_at'),
    )

    def __repr__(self):
        return f"<StockAnalysisCache(symbol='{self.symbol}', company='{self.company_name}', updated='{self.updated_at}')>"


class StockSymbolMapping(Base):
    """기업명 → 심볼 매핑 캐시 테이블"""

    __tablename__ = "stock_symbol_mapping"

    id = Column(Integer, primary_key=True, autoincrement=True)
    input_query = Column(String(200), nullable=False, unique=True, index=True)  # 사용자 입력 (예: "테슬라", "TSLA")
    symbol = Column(String(20), nullable=False)  # 주식 심볼
    company_name = Column(String(200), nullable=False)  # 정식 기업명

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<StockSymbolMapping(query='{self.input_query}' → '{self.symbol}')>"
