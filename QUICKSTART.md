# 빠른 시작 가이드

## 🚀 1분 안에 실행하기

### 💻 로컬 개발 (Docker 없이) - **추천!**

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

**자세한 내용:** [DEVELOPMENT.md](DEVELOPMENT.md)

---

### Production 환경 (API + DB 모두 Docker)

```bash
# 실행
./start-prod.sh

# 또는
docker-compose --env-file .env.prod up -d --build
```

**접속:**
- API: http://localhost:38000
- Docs: http://localhost:38000/docs
- DB: localhost:35432

---

### Local 환경 (API만 Docker, 외부 DB)

```bash
# 실행
./start-local.sh

# 또는
docker-compose -f docker-compose.local.yml --env-file .env.local up -d --build
```

**접속:**
- API: http://localhost:38000
- Docs: http://localhost:38000/docs

---

## 📊 API 테스트

### Swagger UI에서 테스트

1. http://localhost:38000/docs 접속
2. `POST /stock/analyze` 클릭
3. "Try it out" 클릭
4. Request body:
   ```json
   {
     "company": "테슬라"
   }
   ```
5. "Execute" 클릭

### curl로 테스트

```bash
curl -X POST "http://localhost:38000/stock/analyze" \
  -H "Content-Type: application/json" \
  -d '{"company": "테슬라"}'
```

### Python으로 테스트

```python
import requests

response = requests.post(
    "http://localhost:38000/stock/analyze",
    json={"company": "TSLA"}
)

print(response.json())
```

---

## 🛑 중지

### Production

```bash
docker-compose down
```

### Local

```bash
docker-compose -f docker-compose.local.yml down
```

---

## 📝 로그 확인

```bash
# Production
docker-compose logs -f

# Local
docker-compose -f docker-compose.local.yml logs -f

# API만 확인
docker-compose logs -f api
```

---

## 🔧 문제 해결

### 포트 충돌

```bash
# 포트 38000 사용 프로세스 확인
lsof -i :38000

# 포트 35432 사용 프로세스 확인
lsof -i :35432
```

### DB 연결 실패

```bash
# Production: DB 상태 확인
docker-compose ps db

# Local: 외부 DB 연결 테스트
telnet 175.117.82.131 5432
```

### 완전 재시작

```bash
# Production
docker-compose down -v
docker-compose up -d --build

# Local
docker-compose -f docker-compose.local.yml down
docker-compose -f docker-compose.local.yml up -d --build
```

---

## 📚 더 자세한 내용

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - 로컬 개발 가이드 (Docker 없이)
- [DOCKER.md](DOCKER.md) - 전체 Docker 가이드
- [README.md](README.md) - 프로젝트 개요
- [database/README.md](database/README.md) - DB 설정
- [config/README.md](config/README.md) - 검색 소스 설정

---

## 🎯 다음 단계

1. ✅ Docker 실행
2. ✅ API 테스트
3. [ ] 실제 API 키 설정 (.env.prod, .env.local)
4. [ ] 프로덕션 배포 (HTTPS, 도메인 등)
5. [ ] 모니터링 설정

---

## 💡 팁

### 개발 모드 (코드 변경 자동 반영)

`docker-compose.override.yml` 생성:

```yaml
version: '3.8'
services:
  api:
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

그 다음:
```bash
docker-compose up -d
```

### 데이터베이스 백업

```bash
docker exec stock-invest-db pg_dump -U postgres stock_analysis > backup.sql
```

### 컨테이너 내부 접속

```bash
# API 컨테이너
docker exec -it stock-invest-api bash

# DB 컨테이너
docker exec -it stock-invest-db psql -U postgres -d stock_analysis
```
