# 변경 이력

## 2025-11-01

### Docker 서비스명 및 컨테이너명 변경

**변경 전:**
- 서비스: `db`, `api`
- 컨테이너: `stock-analysis-db`, `stock-analysis-api`, `stock-analysis-api-local`
- DB_HOST: `db`

**변경 후:**
- 서비스: `stock-invest-db`, `stock-invest-api`
- 컨테이너: `stock-invest-db`, `stock-invest-api`, `stock-invest-api-local`
- DB_HOST: `stock-invest-db`

**영향 받는 파일:**
- `docker-compose.yml`
- `docker-compose.local.yml`
- `.env.prod`
- 모든 문서 파일 (*.md)
- 모든 실행 스크립트 (*.sh)

**마이그레이션:**

기존 컨테이너가 실행 중이라면:
```bash
# 기존 컨테이너 중지 및 삭제
docker-compose down

# 새로운 이름으로 재시작
docker-compose --env-file .env.prod up -d --build
```

데이터 보존이 필요하다면:
```bash
# 데이터 백업
docker exec stock-analysis-db pg_dump -U postgres stock_analysis > backup.sql

# 기존 컨테이너 삭제
docker-compose down -v

# 새로운 컨테이너 시작
docker-compose --env-file .env.prod up -d --build

# 데이터 복원
cat backup.sql | docker exec -i stock-invest-db psql -U postgres -d stock_analysis
```
