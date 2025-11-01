# Docker 실행 가이드

## 개요

이 프로젝트는 Docker Compose를 사용하여 **Production**과 **Local** 환경을 구분하여 실행할 수 있습니다.

## 포트 매핑

| 서비스 | 내부 포트 | 외부 포트 |
|--------|----------|----------|
| API    | 8000     | **38000** |
| DB     | 5432     | **35432** |

## 환경 구분

### Production 환경
- **DB**: Docker 내부 PostgreSQL 사용
- **DB_HOST**: `db` (Docker Compose alias)
- **설정 파일**: `.env.prod`

### Local 환경
- **DB**: 외부 서버 사용 (175.117.82.131)
- **DB_HOST**: `175.117.82.131`
- **설정 파일**: `.env.local`

---

## 1. 환경 설정

### 1-1. Production 환경 설정

`.env.prod` 파일 수정:

```bash
# .env.prod
OPENAI_API_KEY=sk-proj-your-actual-key-here
BRAVE_API_KEY=your-actual-brave-key-here

DB_HOST=db  # Docker alias
DB_PORT=5432
DB_NAME=stock_analysis
DB_USER=postgres
DB_PASSWORD=your-secure-password
```

### 1-2. Local 환경 설정

`.env.local` 파일 수정:

```bash
# .env.local
OPENAI_API_KEY=sk-proj-your-actual-key-here
BRAVE_API_KEY=your-actual-brave-key-here

DB_HOST=175.117.82.131  # 외부 서버
DB_PORT=5432
DB_NAME=stock_analysis
DB_USER=postgres
DB_PASSWORD=your-db-password
```

---

## 2. 실행 방법

### 🚀 Production 환경 실행 (API + DB)

```bash
# 1. 이미지 빌드 및 서비스 시작
docker-compose --env-file .env.prod up -d --build

# 2. 로그 확인
docker-compose logs -f

# 3. 상태 확인
docker-compose ps

# 4. 종료
docker-compose down
```

**접속:**
- API: http://localhost:38000
- API Docs: http://localhost:38000/docs
- DB: localhost:35432

---

### 🏠 Local 환경 실행 (API만, 외부 DB 사용)

```bash
# 1. 이미지 빌드 및 서비스 시작
docker-compose -f docker-compose.local.yml --env-file .env.local up -d --build

# 2. 로그 확인
docker-compose -f docker-compose.local.yml logs -f

# 3. 종료
docker-compose -f docker-compose.local.yml down
```

**접속:**
- API: http://localhost:38000
- API Docs: http://localhost:38000/docs

---

## 3. 주요 명령어

### 빌드 및 실행

```bash
# Production (DB 포함)
docker-compose --env-file .env.prod up -d --build

# Local (API만)
docker-compose -f docker-compose.local.yml --env-file .env.local up -d --build
```

### 로그 확인

```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f api
docker-compose logs -f db
```

### 서비스 재시작

```bash
# 전체 재시작
docker-compose restart

# API만 재시작
docker-compose restart api
```

### 컨테이너 접속

```bash
# API 컨테이너 접속
docker exec -it stock-invest-api bash

# DB 컨테이너 접속
docker exec -it stock-invest-db psql -U postgres -d stock_analysis
```

### 데이터베이스 관리

```bash
# DB 백업
docker exec stock-invest-db pg_dump -U postgres stock_analysis > backup.sql

# DB 복원
cat backup.sql | docker exec -i stock-invest-db psql -U postgres -d stock_analysis
```

### 정리

```bash
# 컨테이너 중지 및 삭제
docker-compose down

# 볼륨까지 삭제 (데이터 삭제 주의!)
docker-compose down -v

# 이미지까지 삭제
docker-compose down --rmi all
```

---

## 4. 트러블슈팅

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
lsof -i :38000
lsof -i :35432

# 프로세스 종료
kill -9 <PID>
```

### DB 연결 실패 (Production)

```bash
# DB 상태 확인
docker-compose ps db

# DB 로그 확인
docker-compose logs db

# DB 헬스체크
docker exec stock-invest-db pg_isready -U postgres
```

### DB 연결 실패 (Local)

```bash
# 외부 DB 연결 테스트
psql -h 175.117.82.131 -p 5432 -U postgres -d stock_analysis

# 방화벽 확인
telnet 175.117.82.131 5432
```

### 빌드 실패

```bash
# 캐시 없이 재빌드
docker-compose build --no-cache

# 이미지 삭제 후 재빌드
docker-compose down --rmi all
docker-compose up -d --build
```

### 컨테이너 실행 안됨

```bash
# 상세 로그 확인
docker-compose logs --tail=100 api

# 컨테이너 직접 실행 (디버깅)
docker run -it --rm stock-invest-api bash
```

---

## 5. 개발 팁

### 코드 변경 시 재시작

```bash
# API만 재빌드 및 재시작
docker-compose up -d --build api
```

### 로컬 개발 모드 (Hot Reload)

`docker-compose.override.yml` 생성:

```yaml
version: '3.8'
services:
  api:
    volumes:
      - .:/app  # 소스 코드 마운트
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 환경 변수 확인

```bash
# 컨테이너 내부 환경 변수 확인
docker exec stock-invest-api env | grep DB_
```

---

## 6. 배포 체크리스트

- [ ] `.env.prod` 파일에 실제 API 키 설정
- [ ] DB 비밀번호 변경 (기본값 사용 금지)
- [ ] 방화벽 설정 (38000, 35432 포트)
- [ ] HTTPS 설정 (nginx 리버스 프록시 권장)
- [ ] 로그 모니터링 설정
- [ ] 백업 스케줄 설정

---

## 7. 아키텍처

### Production
```
┌─────────────────────────────────────┐
│         Docker Network              │
│                                     │
│  ┌──────────┐      ┌──────────┐    │
│  │   API    │─────▶│    DB    │    │
│  │  :8000   │      │  :5432   │    │
│  └──────────┘      └──────────┘    │
│       │                  │          │
└───────┼──────────────────┼──────────┘
        │                  │
   38000│             35432│
        ▼                  ▼
    Host:38000       Host:35432
```

### Local
```
┌──────────────────┐        ┌──────────────────┐
│  Docker Network  │        │  외부 서버       │
│                  │        │                  │
│  ┌──────────┐    │        │  ┌──────────┐    │
│  │   API    │────┼───────▶│  │    DB    │    │
│  │  :8000   │    │        │  │  :5432   │    │
│  └──────────┘    │        │  └──────────┘    │
│       │          │        │                  │
└───────┼──────────┘        └──────────────────┘
        │                   175.117.82.131:5432
   38000│
        ▼
    Host:38000
```

---

## 8. 참고 자료

- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [PostgreSQL Docker Hub](https://hub.docker.com/_/postgres)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/docker/)
