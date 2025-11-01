# Stock Analysis API

OpenAI GPT-5를 사용하여 주식을 종합 분석하고 투자 의견을 제공하는 FastAPI 프로젝트입니다.

## 설치

```bash
# 의존성 설치
uv sync
```

## 환경 설정

`.env` 파일을 생성하고 API 키들을 설정하세요:

```bash
cp .env.example .env
```

`.env` 파일에 실제 API 키를 입력하세요:
```
OPENAI_API_KEY=sk-proj-your-actual-api-key-here
BRAVE_API_KEY=your-brave-api-key-here
```

### API 키 발급

1. **OpenAI API 키**: https://platform.openai.com/api-keys
2. **Brave Search API 키** (선택사항): https://brave.com/search/api/
   - MCP를 통한 실시간 웹 검색 기능 활성화
   - 없으면 GPT-5의 기본 지식으로만 분석

## 실행

```bash
# 서버 실행
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --reload
```

서버는 `http://localhost:8000`에서 실행됩니다.

## API 엔드포인트

### 1. GET `/`
서버 상태 확인

### 2. POST `/api/stock/analyze`
주식 종목을 종합 분석하고 매수/매도/홀딩 추천 제공

**요청 예시:**
```json
{
  "company": "테슬라"
}
```

또는

```json
{
  "company": "TSLA"
}
```

**응답 예시:**
```json
{
  "symbol": "TSLA",
  "recommendation": "BUY",
  "reason": "- 최근 1개월간 꾸준한 상승세\n- 신제품 출시로 인한 긍정적 전망\n- 안정적인 재무 상태",
  "analysis": "테슬라(TSLA)는 지난 1년간 30% 상승했으며..."
}
```

### 3. GET `/api/stock/{company}`
특정 주식 종목을 종합 분석 (간편한 GET 방식)
기업명 또는 심볼 모두 사용 가능

**요청 예시:**
```
GET /api/stock/엔비디아
```

또는

```
GET /api/stock/NVDA
```

**응답 예시:**
```json
{
  "symbol": "NVDA",
  "recommendation": "HOLD",
  "reason": "- 변동성이 큰 시장 상황\n- 경쟁 심화로 인한 불확실성\n- 장기적으론 성장 가능성 있음",
  "analysis": "엔비디아(NVDA)는 지난 6개월간 횡보세를 보이고 있으며..."
}
```

## AI 분석 항목

GPT-5가 다음 항목들을 종합 분석합니다:

1. **기간별 거래 내역 분석**: 1년, 6개월, 3개월, 1개월, 1주일, 3일, 1일
2. **경제 뉴스**: 관련 경제 동향 및 시장 이슈
3. **정치적 요인**: 규제 변화 및 정책 영향
4. **기업 실적**: 재무 상태 및 성과
5. **산업 전망**: 경쟁 환경 및 미래 전망

**추천 결과**:
- **단기 (1일~1주일)**: BUY/SELL/HOLD
- **중기 (1주일~3개월)**: BUY/SELL/HOLD
- **장기 (3개월~1년)**: BUY/SELL/HOLD

## MCP (Model Context Protocol) 통합

이 프로젝트는 MCP를 통해 OpenAI GPT-5에게 실시간 정보를 제공합니다.

### MCP란?

MCP(Model Context Protocol)는 AI 모델이 외부 데이터 소스와 통신할 수 있게 해주는 프로토콜입니다. 이를 통해:

- 실시간 웹 검색 (Brave Search API 사용)
- 최신 뉴스 및 주가 정보 수집
- 정확한 날짜 기반 분석

### MCP 활성화

1. `BRAVE_API_KEY`를 `.env`에 설정하면 자동으로 MCP 활성화
2. API가 필요한 경우 자동으로 웹 검색 실행
3. 검색 결과를 바탕으로 더 정확한 분석 제공

### MCP 없이 사용

`BRAVE_API_KEY`가 없어도 GPT-5의 기본 지식으로 분석이 가능합니다. 단, 최신 정보는 제한적입니다.

## API 문서

서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 테스트 예시

### cURL로 테스트:
```bash
# POST 방식 - 기업명으로 요청
curl -X POST "http://localhost:8000/api/stock/analyze" \
  -H "Content-Type: application/json" \
  -d '{"company":"테슬라"}'

# POST 방식 - 심볼로 요청
curl -X POST "http://localhost:8000/api/stock/analyze" \
  -H "Content-Type: application/json" \
  -d '{"company":"AAPL"}'

# GET 방식 - 기업명
curl "http://localhost:8000/api/stock/엔비디아"

# GET 방식 - 심볼
curl "http://localhost:8000/api/stock/NVDA"
```

### Python으로 테스트:
```python
import requests

# POST 방식 - 기업명
response = requests.post(
    "http://localhost:8000/api/stock/analyze",
    json={"company": "테슬라"}
)
print(response.json())

# POST 방식 - 심볼
response = requests.post(
    "http://localhost:8000/api/stock/analyze",
    json={"company": "TSLA"}
)
print(response.json())

# GET 방식 - 기업명
response = requests.get("http://localhost:8000/api/stock/엔비디아")
print(response.json())

# GET 방식 - 심볼
response = requests.get("http://localhost:8000/api/stock/NVDA")
print(response.json())
```

## 사용 기술

- **FastAPI**: 고성능 웹 프레임워크
- **OpenAI GPT-5**: AI 기반 주식 분석
- **MCP (Model Context Protocol)**: 실시간 정보 연동
- **Brave Search API**: 웹 검색을 통한 최신 정보 수집
- **Uvicorn**: ASGI 서버
- **Python-dotenv**: 환경 변수 관리

## 프로젝트 구조

```
invest-test/
├── agents/
│   └── openai_agent.py      # OpenAI + MCP 통합 에이전트
├── api/
│   └── stock_api.py          # FastAPI 라우터
├── models/
│   └── stock.py              # 데이터 모델
├── services/
│   └── stock_service.py      # 비즈니스 로직
├── main.py                   # 애플리케이션 엔트리포인트
├── .env                      # 환경 변수 (직접 생성)
├── .env.example              # 환경 변수 예시
└── README.md
```
