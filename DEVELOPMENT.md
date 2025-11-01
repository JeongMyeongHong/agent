# 로컬 개발 가이드

## 🏠 Docker 없이 로컬에서 실행하기

### 빠른 시작 (추천)

```bash
# 1. 의존성 설치
uv sync

# 2. 실행
./run.sh

# 또는
python main.py
```

**접속:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 📋 사전 요구사항

### 필수

1. **Python 3.13**
   ```bash
   python --version  # 3.13 확인
   ```

2. **uv** (Python 패키지 매니저)
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # 또는 pip
   pip install uv
   ```

### 선택 (MCP 웹 검색용)

3. **Node.js & npm** (Brave Search MCP용)
   ```bash
   # macOS
   brew install node

   # 확인
   node --version
   npm --version
   ```

---

## 🚀 실행 방법

### 방법 1: 간단 실행 (추천)

```bash
./run.sh
```

### 방법 2: 상세 실행

```bash
./start-dev.sh
```

이 스크립트는 자동으로:
- .env.local → .env 복사
- 가상환경 확인/생성
- 의존성 설치
- DB 연결 테스트
- 애플리케이션 실행

### 방법 3: 수동 실행

```bash
# 1. 환경 변수 설정
cp .env.local .env

# 2. 의존성 설치
uv sync

# 3. 실행
python main.py
```

### 방법 4: 개발 모드 (Hot Reload)

```bash
# uvicorn으로 직접 실행 (코드 변경 시 자동 재시작)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔧 환경 설정

### 환경 변수 파일

로컬 개발 시 `.env` 또는 `.env.local` 사용:

```bash
# .env (로컬 개발용)
OPENAI_API_KEY=sk-proj-...
BRAVE_API_KEY=BSA7xd-...

DB_HOST=175.117.82.131  # 외부 DB
DB_PORT=5432
DB_NAME=stock_analysis
DB_USER=postgres
DB_PASSWORD=postgres
```

### 데이터베이스

로컬 개발 시 외부 DB 사용:
- **호스트**: 175.117.82.131
- **포트**: 5432

**연결 테스트:**
```bash
# psql로 연결 테스트
psql -h 175.117.82.131 -p 5432 -U postgres -d stock_analysis

# 또는 Python으로
python -c "from database import init_db; init_db()"
```

---

## 📦 의존성 관리

### uv 사용 (추천)

```bash
# 의존성 설치
uv sync

# 패키지 추가
uv add fastapi

# 개발 의존성 추가
uv add --dev pytest
```

### pip 사용

```bash
# 의존성 설치
pip install -e .

# 또는
pip install -r requirements.txt  # 있다면
```

---

## 🧪 개발 워크플로우

### 1. 코드 변경

```bash
# 에디터로 코드 수정
code .  # VS Code
```

### 2. 자동 재시작 모드로 실행

```bash
uvicorn main:app --reload
```

### 3. API 테스트

```bash
# Swagger UI
open http://localhost:8000/docs

# curl
curl -X POST http://localhost:8000/stock/analyze \
  -H "Content-Type: application/json" \
  -d '{"company": "TSLA"}'
```

### 4. 로그 확인

터미널에서 실시간 로그 확인 가능

---

## 🐛 디버깅

### VS Code 디버그 설정

`.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "debugpy",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "main:app",
        "--reload",
        "--port",
        "8000"
      ],
      "jinja": true,
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### Python 디버거

```python
# 코드에 브레이크포인트 추가
import pdb; pdb.set_trace()

# 또는
breakpoint()
```

---

## 🔍 로그 레벨 조정

main.py에서:

```python
import logging

# 개발 시 DEBUG 레벨
logging.basicConfig(level=logging.DEBUG)
```

---

## 📊 데이터베이스 관리

### 로컬 DB 조회

```bash
# psql 접속
psql -h 175.117.82.131 -p 5432 -U postgres -d stock_analysis

# SQL 실행
SELECT * FROM stock_analysis_cache ORDER BY updated_at DESC LIMIT 10;
```

### DB 초기화

```python
from database import init_db
init_db()
```

### 캐시 확인

```python
from database import get_db, StockRepository

with get_db() as db:
    repo = StockRepository(db)

    # 심볼 매핑 확인
    mapping = repo.get_symbol_mapping("테슬라")
    print(mapping)

    # 분석 캐시 확인
    analysis = repo.get_cached_analysis("TSLA")
    print(analysis)
```

---

## 🚦 환경 구분

| 환경 | 실행 방법 | 포트 | DB | 용도 |
|------|----------|------|-----|------|
| **Dev** | `./run.sh` | 8000 | 외부 | 로컬 개발 |
| **Local** | `./start-local.sh` | 38000 | 외부 | Docker 테스트 |
| **Prod** | `./start-prod.sh` | 38000 | Docker | 배포 |

---

## 🔄 개발 팁

### Hot Reload 켜기

```bash
uvicorn main:app --reload --log-level debug
```

### 특정 포트로 실행

```bash
uvicorn main:app --port 3000
```

### 외부 접속 허용

```bash
uvicorn main:app --host 0.0.0.0
```

### 워커 수 조정

```python
# main.py
uvicorn.run("main:app", workers=1)  # 개발 시 1개
```

---

## 🧹 정리

### 캐시 삭제

```bash
# Python 캐시
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# UV 캐시
rm -rf .uv
```

### 가상환경 재생성

```bash
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
uv sync
```

---

## ⚡ 빠른 명령어 모음

```bash
# 실행
./run.sh                              # 기본 실행
./start-dev.sh                        # 상세 실행
python main.py                        # 직접 실행
uvicorn main:app --reload            # Hot Reload

# 의존성
uv sync                               # 설치
uv add package-name                  # 추가

# DB
psql -h 175.117.82.131 -p 5432 -U postgres -d stock_analysis

# 테스트
curl -X POST http://localhost:8000/stock/analyze \
  -H "Content-Type: application/json" \
  -d '{"company": "TSLA"}'

# 로그
tail -f logs/app.log                 # 로그 파일이 있다면
```

---

## 📚 다음 단계

1. ✅ 로컬 실행
2. [ ] 코드 수정
3. [ ] 테스트 작성
4. [ ] Docker로 빌드 테스트
5. [ ] Production 배포

---

## 💡 자주 묻는 질문

### Q: Node.js가 없으면?
A: MCP Brave Search만 안 되고 나머지는 정상 동작합니다.

### Q: DB 연결 안될 때?
A: 방화벽 확인 또는 로컬 PostgreSQL 사용:
```bash
brew install postgresql@15
brew services start postgresql@15
createdb stock_analysis
# .env에서 DB_HOST=localhost로 변경
```

### Q: 포트 8000이 이미 사용 중?
A: 다른 포트 사용:
```bash
uvicorn main:app --port 8001
```

### Q: 의존성 설치 실패?
A: pip으로 직접 설치:
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary openai python-dotenv httpx mcp
```

---

## 🎯 체크리스트

개발 시작 전:
- [ ] Python 3.13 설치
- [ ] uv 설치
- [ ] Node.js 설치 (선택)
- [ ] .env.local 설정
- [ ] DB 연결 확인
- [ ] 의존성 설치 (uv sync)
- [ ] 실행 테스트 (./run.sh)
