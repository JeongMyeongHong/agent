import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 환경 변수 로드
load_dotenv()


class OpenAIAgent:
    """OpenAI GPT-5와 MCP를 통합한 에이전트"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-5"
        self.mcp_sessions: Dict[str, ClientSession] = {}
        self.mcp_tools: List[Dict[str, Any]] = []

    async def initialize_mcp(self):
        """MCP 서버 초기화 및 연결"""
        try:
            # Brave Search MCP 서버 연결
            brave_api_key = os.getenv("BRAVE_API_KEY")
            if brave_api_key:
                await self._connect_brave_search(brave_api_key)
                print("[MCP] Brave Search 연결 완료")
            else:
                print("[MCP] BRAVE_API_KEY가 설정되지 않았습니다. 웹 검색 기능이 비활성화됩니다.")
        except Exception as e:
            print(f"[MCP] 초기화 중 오류 발생: {e}")

    async def _connect_brave_search(self, api_key: str):
        """Brave Search MCP 서버에 연결"""
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-brave-search"],
            env={"BRAVE_API_KEY": api_key}
        )

        stdio_transport = await stdio_client(server_params)
        stdio, write = stdio_transport
        session = ClientSession(stdio, write)

        await session.initialize()
        self.mcp_sessions["brave-search"] = session

        # 도구 목록 가져오기
        tools_list = await session.list_tools()
        for tool in tools_list.tools:
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema
                }
            }
            self.mcp_tools.append(openai_tool)

    async def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """MCP 도구 호출"""
        for session in self.mcp_sessions.values():
            try:
                result = await session.call_tool(tool_name, arguments)
                if result and hasattr(result, 'content'):
                    contents = []
                    for content in result.content:
                        if hasattr(content, 'text'):
                            contents.append(content.text)
                    return "\n".join(contents)
            except Exception as e:
                print(f"[MCP] 도구 호출 오류 ({tool_name}): {e}")
        return ""

    async def cleanup_mcp(self):
        """MCP 세션 정리"""
        for session in self.mcp_sessions.values():
            try:
                await session.__aexit__(None, None, None)
            except:
                pass
        self.mcp_sessions.clear()
        self.mcp_tools.clear()

    def get_stock_symbol(self, company: str) -> str:
        """
        기업명이나 심볼을 정확한 주식 티커 심볼로 변환

        Args:
            company: 기업명 또는 심볼 (예: "테슬라", "TSLA")

        Returns:
            정확한 주식 티커 심볼 (예: "TSLA")
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """당신은 주식 심볼 전문가입니다.
사용자가 입력한 기업명이나 심볼을 정확한 주식 티커 심볼로 변환해주세요.
예시:
- "테슬라" → "TSLA"
- "엔비디아" → "NVDA"
- "애플" → "AAPL"
- "삼성전자" → "005930.KS"
- "SK하이닉스" → "000660.KS"

반드시 심볼만 답변하고 다른 설명은 하지 마세요."""
                },
                {
                    "role": "user",
                    "content": f"{company}"
                }
            ],
            max_completion_tokens=500
        )

        print(f"[DEBUG] Symbol response finish_reason: {response.choices[0].finish_reason}")
        print(f"[DEBUG] Symbol response content: '{response.choices[0].message.content}'")

        result = response.choices[0].message.content
        if result:
            return result.strip()
        else:
            print(f"[ERROR] Empty symbol result for company: {company}")
            return company  # 심볼을 찾지 못하면 입력값 그대로 반환

    async def analyze_stock_with_mcp(self, symbol: str, company: str) -> str:
        """
        MCP를 사용하여 최신 정보를 포함한 주식 종합 분석

        Args:
            symbol: 주식 티커 심볼 (예: "TSLA")
            company: 원래 입력된 기업명 (예: "테슬라")

        Returns:
            AI가 생성한 분석 텍스트
        """
        messages = [
            {
                "role": "system",
                "content": """당신은 전문 주식 투자 분석가입니다.
사용자가 제공한 주식 종목에 대해 단기, 중기, 장기로 구분하여 투자 의견을 제시해야 합니다.

최신 정보가 필요하면 brave_web_search 도구를 사용하여 다음을 검색하세요:
1. 최신 주가 동향 및 거래량
2. 최근 뉴스 및 공시사항
3. 경제/정치적 이슈
4. 산업 트렌드
5. 기업 실적 발표

분석 후 반드시 다음 형식으로 답변하세요:

**단기 투자 의견 (1일~1주일)**: [BUY/SELL/HOLD 중 하나]
**단기 이유**:
- [이유 1]
- [이유 2]
- [이유 3]

**중기 투자 의견 (1주일~3개월)**: [BUY/SELL/HOLD 중 하나]
**중기 이유**:
- [이유 1]
- [이유 2]
- [이유 3]

**장기 투자 의견 (3개월~1년)**: [BUY/SELL/HOLD 중 하나]
**장기 이유**:
- [이유 1]
- [이유 2]
- [이유 3]

**종합 분석**:
[최신 정보를 바탕으로 한 상세 분석]"""
            },
            {
                "role": "user",
                "content": f"{symbol} ({company}) 주식에 대한 최신 정보를 검색하고 종합 분석과 투자 의견을 제시해주세요."
            }
        ]

        # MCP 도구가 있으면 함께 전달
        tools = self.mcp_tools if self.mcp_tools else None

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            max_completion_tokens=5000
        )

        # 도구 호출이 있는지 확인
        while response.choices[0].finish_reason == "tool_calls":
            tool_calls = response.choices[0].message.tool_calls
            messages.append(response.choices[0].message)

            # 각 도구 호출 처리
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                print(f"[MCP] 도구 호출: {tool_name} - {tool_args}")

                # MCP 도구 실행 (비동기)
                tool_result = await self._call_mcp_tool(tool_name, tool_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

            # 다음 응답 생성
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                max_completion_tokens=5000
            )

        return response.choices[0].message.content

    def analyze_stock(self, symbol: str, company: str) -> str:
        """
        주식 종목을 종합 분석 (기존 방식 - MCP 없이)

        Args:
            symbol: 주식 티커 심볼 (예: "TSLA")
            company: 원래 입력된 기업명 (예: "테슬라")

        Returns:
            AI가 생성한 분석 텍스트
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": """당신은 전문 주식 투자 분석가입니다.
사용자가 제공한 주식 종목에 대해 단기, 중기, 장기로 구분하여 투자 의견을 제시해야 합니다.

다음 항목들을 철저히 분석하세요:
1. 기간별 거래 내역 및 가격 추세 분석 (1년, 6개월, 3개월, 1개월, 1주일, 3일, 1일)
2. 관련 경제 뉴스 및 시장 동향
3. 정치적 요인 및 규제 변화
4. 기업 실적 및 재무 상태
5. 산업 전망 및 경쟁 환경

분석 후 반드시 다음 형식으로 답변하세요:

**단기 투자 의견 (1일~1주일)**: [BUY/SELL/HOLD 중 하나]
**단기 이유**:
- [이유 1]
- [이유 2]
- [이유 3]

**중기 투자 의견 (1주일~3개월)**: [BUY/SELL/HOLD 중 하나]
**중기 이유**:
- [이유 1]
- [이유 2]
- [이유 3]

**장기 투자 의견 (3개월~1년)**: [BUY/SELL/HOLD 중 하나]
**장기 이유**:
- [이유 1]
- [이유 2]
- [이유 3]

**종합 분석**:
[기간별 거래 패턴, 뉴스 분석, 경제/정치적 요인을 포함한 상세 분석]"""
                },
                {
                    "role": "user",
                    "content": f"{symbol} ({company}) 주식에 대한 종합 분석과 투자 의견을 제시해주세요."
                }
            ],
            max_completion_tokens=5000
        )

        return response.choices[0].message.content
