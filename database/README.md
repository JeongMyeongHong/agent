# Database Setup Guide

## PostgreSQL 데이터베이스 설정

### 1. PostgreSQL 설치 (Docker 사용 권장)

```bash
# Docker로 PostgreSQL 실행
docker run -d \
  --name stock-invest-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=stock_analysis \
  -p 5432:5432 \
  postgres:15-alpine
```

### 2. 환경 변수 설정

`.env` 파일에 다음 설정이 포함되어 있는지 확인:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=stock_analysis
DB_USER=postgres
DB_PASSWORD=postgres
```

### 3. 데이터베이스 초기화

애플리케이션 시작 시 자동으로 테이블이 생성됩니다:

```bash
# 의존성 설치
uv sync

# 애플리케이션 실행 (자동으로 DB 초기화)
uv run python main.py
```

## 데이터베이스 스키마

### stock_symbol_mapping (심볼 매핑 캐시)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | Primary Key |
| input_query | VARCHAR(200) | 사용자 입력 (예: "테슬라") |
| symbol | VARCHAR(20) | 주식 심볼 (예: "TSLA") |
| company_name | VARCHAR(200) | 정식 기업명 |
| created_at | TIMESTAMP | 생성 시간 |
| updated_at | TIMESTAMP | 수정 시간 |

### stock_analysis_cache (분석 결과 캐시)

| 컬럼 | 타입 | 설명 |
|------|------|------|
| id | INTEGER | Primary Key |
| symbol | VARCHAR(20) | 주식 심볼 |
| company_name | VARCHAR(200) | 정식 기업명 |
| short_term_action | VARCHAR(10) | 단기 투자 의견 |
| short_term_reason | TEXT | 단기 이유 |
| mid_term_action | VARCHAR(10) | 중기 투자 의견 |
| mid_term_reason | TEXT | 중기 이유 |
| long_term_action | VARCHAR(10) | 장기 투자 의견 |
| long_term_reason | TEXT | 장기 이유 |
| analysis | TEXT | 종합 분석 |
| created_at | TIMESTAMP | 생성 시간 |
| updated_at | TIMESTAMP | 수정 시간 |

## 캐시 정책

- **심볼 매핑**: 한번 변환된 기업명→심볼 매핑은 영구 저장
- **분석 결과**: 기본 24시간 캐시 (StockService.cache_hours로 조정 가능)
- **자동 정리**: 30일 이상 된 분석 결과는 수동 삭제 필요

## 관리 명령어

```bash
# PostgreSQL 접속
docker exec -it stock-invest-db psql -U postgres -d stock_analysis

# 테이블 확인
\dt

# 데이터 조회
SELECT * FROM stock_symbol_mapping;
SELECT * FROM stock_analysis_cache ORDER BY updated_at DESC LIMIT 10;

# 캐시 삭제 (30일 이상)
DELETE FROM stock_analysis_cache WHERE updated_at < NOW() - INTERVAL '30 days';
```

## 트러블슈팅

### 연결 실패 시

1. PostgreSQL이 실행 중인지 확인:
   ```bash
   docker ps | grep stock-invest-db
   ```

2. 포트 확인:
   ```bash
   lsof -i :5432
   ```

3. 환경 변수 확인:
   ```bash
   cat .env | grep DB_
   ```

### 테이블이 생성되지 않는 경우

Python으로 수동 초기화:

```python
from database import init_db
init_db()
```
