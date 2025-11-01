import asyncio
from agents import OpenAIAgent
from models import StockResponse, RecommendationDetail
from database import get_db, StockRepository


class StockService:
    """주식 분석 비즈니스 로직을 처리하는 서비스"""

    def __init__(self):
        self.agent = OpenAIAgent()
        self._mcp_initialized = False
        self.cache_enabled = True  # 캐시 사용 여부
        self.cache_hours = 24  # 캐시 유효 시간 (시간 단위)

    async def _ensure_mcp_initialized(self):
        """MCP가 초기화되지 않았다면 초기화"""
        if not self._mcp_initialized:
            await self.agent.initialize_mcp()
            self._mcp_initialized = True

    async def analyze_stock_async(self, company: str, use_mcp: bool = True, use_cache: bool = True) -> StockResponse:
        """
        주식을 종합 분석하고 투자 의견을 제공 (비동기)

        Args:
            company: 기업명 또는 심볼 (예: "테슬라", "TSLA")
            use_mcp: MCP를 사용하여 최신 정보 검색 여부
            use_cache: 캐시 사용 여부

        Returns:
            StockResponse: 분석 결과
        """
        # 데이터베이스 세션
        with get_db() as db:
            repo = StockRepository(db)

            # 1단계: 기업명/심볼을 정확한 주식 심볼과 정식 기업명으로 변환 (캐시 활용)
            stock_symbol, company_name = self._get_stock_info_with_cache(company, repo)

            # 2단계: 캐시된 분석 결과 확인
            if use_cache and self.cache_enabled:
                cached_result = repo.get_cached_analysis(stock_symbol, self.cache_hours)
                if cached_result:
                    print(f"[CACHE HIT] {stock_symbol} ({company_name}) - 캐시된 결과 반환")
                    return cached_result
                else:
                    print(f"[CACHE MISS] {stock_symbol} ({company_name}) - 새로 분석 시작")

            # 3단계: MCP 초기화
            if use_mcp:
                await self._ensure_mcp_initialized()

            # 4단계: 주식 종합 분석 (AI 호출)
            if use_mcp and self.agent.mcp_tools:
                analysis_text = await self.agent.analyze_stock_with_mcp(stock_symbol, company_name)
            else:
                analysis_text = self.agent.analyze_stock(stock_symbol, company_name)

            print(f"\n{'='*80}")
            print(f"[DEBUG] AI 전체 응답:")
            print(f"{'='*80}")
            print(analysis_text)
            print(f"{'='*80}\n")

            # 5단계: 응답 파싱
            short_term = self._parse_recommendation_detail(analysis_text, "단기")
            mid_term = self._parse_recommendation_detail(analysis_text, "중기")
            long_term = self._parse_recommendation_detail(analysis_text, "장기")
            analysis_detail = self._parse_analysis(analysis_text)

            print(f"[DEBUG] Parsed short_term: {short_term}")
            print(f"[DEBUG] Parsed mid_term: {mid_term}")
            print(f"[DEBUG] Parsed long_term: {long_term}")

            response = StockResponse(
                symbol=stock_symbol,
                company_name=company_name,
                short_term=short_term,
                mid_term=mid_term,
                long_term=long_term,
                analysis=analysis_detail
            )

            # 6단계: 분석 결과 캐시 저장
            if use_cache and self.cache_enabled:
                repo.save_analysis(response)
                print(f"[CACHE SAVE] {stock_symbol} 분석 결과 저장 완료")

            return response

    def _get_stock_info_with_cache(self, company: str, repo: StockRepository) -> tuple[str, str]:
        """
        캐시를 활용한 심볼 변환

        Args:
            company: 사용자 입력
            repo: StockRepository 인스턴스

        Returns:
            (심볼, 정식 기업명) 튜플
        """
        # 캐시 확인
        cached_mapping = repo.get_symbol_mapping(company)
        if cached_mapping:
            print(f"[SYMBOL CACHE HIT] {company} → {cached_mapping[0]}")
            return cached_mapping

        # AI로 변환
        print(f"[SYMBOL CACHE MISS] {company} - AI로 변환 중...")
        stock_symbol, company_name = self.agent.get_stock_info(company)

        # 캐시 저장
        repo.save_symbol_mapping(company, stock_symbol, company_name)
        print(f"[SYMBOL CACHE SAVE] {company} → {stock_symbol} 저장 완료")

        return (stock_symbol, company_name)

    def analyze_stock(self, company: str, use_mcp: bool = True, use_cache: bool = True) -> StockResponse:
        """
        주식을 종합 분석하고 투자 의견을 제공 (동기 래퍼)

        Args:
            company: 기업명 또는 심볼 (예: "테슬라", "TSLA")
            use_mcp: MCP를 사용하여 최신 정보 검색 여부
            use_cache: 캐시 사용 여부

        Returns:
            StockResponse: 분석 결과
        """
        # 비동기 함수를 동기적으로 실행
        return asyncio.run(self.analyze_stock_async(company, use_mcp, use_cache))

    def _parse_recommendation_detail(self, text: str, term: str) -> RecommendationDetail:
        """
        특정 기간(단기/중기/장기)의 투자 의견과 이유를 파싱

        Args:
            text: AI 응답 텍스트
            term: "단기", "중기", "장기"

        Returns:
            RecommendationDetail: 투자 의견과 이유
        """
        # 투자 의견 파싱
        action = "HOLD"  # 기본값
        sections = text.split("**")

        for i, section in enumerate(sections):
            if f"{term} 투자 의견" in section:
                if i + 1 < len(sections):
                    content = sections[i + 1].strip()
                    if "BUY" in content.upper():
                        action = "BUY"
                    elif "SELL" in content.upper():
                        action = "SELL"
                    elif "HOLD" in content.upper():
                        action = "HOLD"
                break

        # 이유 파싱
        reason = ""
        for i, section in enumerate(sections):
            if f"{term} 이유" in section:
                if i + 1 < len(sections):
                    reason = sections[i + 1].strip()
                break

        # 파싱 실패 시 기본값
        if not reason:
            reason = f"{term} 투자 의견 분석 중"

        return RecommendationDetail(action=action, reason=reason)

    def _parse_analysis(self, text: str) -> str:
        """종합 분석 파싱"""
        sections = text.split("**")
        for i, section in enumerate(sections):
            if "종합 분석" in section:
                if i + 1 < len(sections):
                    return sections[i + 1].strip()
        # 파싱 실패 시 전체 텍스트 반환
        return text
