# 배포 가이드

## 🚀 자동 배포 (Jenkins 없이)

### 초간단 배포

서버에서 단 한 줄로 배포:

```bash
curl -sSL https://raw.githubusercontent.com/JeongMyeongHong/agent/main/deploy.sh | bash
```

또는 수동으로:

```bash
# 1. 스크립트 다운로드
wget https://raw.githubusercontent.com/JeongMyeongHong/agent/main/deploy.sh
chmod +x deploy.sh

# 2. 실행
./deploy.sh
```

---

## 📋 사전 요구사항

### 필수

1. **Docker & Docker Compose**
   ```bash
   # Docker 설치 확인
   docker --version
   docker-compose --version
   ```

2. **Git**
   ```bash
   git --version
   ```

### 권장

- **포트 열기**: 38000 (API), 35432 (DB)
- **방화벽 설정**

---

## 🎯 배포 방법

### 방법 1: 자동 배포 스크립트 (추천)

```bash
# GitHub에서 자동으로 clone하고 배포
./deploy.sh
```

**이 스크립트가 하는 일:**
1. ✅ `/root/stock-invest`에 코드 clone
2. ✅ 기존 컨테이너 중지
3. ✅ 최신 코드 pull
4. ✅ 환경 변수 확인
5. ✅ Docker 이미지 빌드
6. ✅ 컨테이너 시작
7. ✅ 헬스체크
8. ✅ 상태 확인

---

### 방법 2: 수동 배포

```bash
# 1. 코드 다운로드
git clone https://github.com/JeongMyeongHong/agent.git /root/stock-invest
cd /root/stock-invest

# 2. 환경 변수 설정
cp .env.example .env.prod
nano .env.prod  # API 키 설정

# 3. 배포
./start-prod.sh
```

---

## 🔄 업데이트

### 최신 코드로 업데이트

```bash
./update.sh
```

또는:

```bash
cd /root/stock-invest
git pull origin main
docker-compose down
docker-compose --env-file .env.prod up -d --build
```

---

## 🔧 배포 디렉토리 변경

기본 배포 위치: `/root/stock-invest`

변경하려면 `deploy.sh` 수정:

```bash
# deploy.sh
DEPLOY_DIR="/your/custom/path"  # 이 부분 수정
```

---

## 🔑 환경 변수 설정

배포 후 **반드시** API 키를 설정하세요:

```bash
# 배포 디렉토리로 이동
cd /root/stock-invest

# .env.prod 편집
nano .env.prod
```

**필수 설정:**
```env
OPENAI_API_KEY=sk-proj-your-actual-key
BRAVE_API_KEY=your-brave-key
DB_HOST=stock-invest-db
DB_PASSWORD=secure-password  # 기본값 변경!
```

설정 후 재시작:
```bash
docker-compose restart
```

---

## 📊 배포 확인

### 상태 확인

```bash
cd /root/stock-invest
docker-compose ps
```

예상 출력:
```
NAME                   STATUS              PORTS
stock-invest-api       Up 2 minutes        0.0.0.0:38000->8000/tcp
stock-invest-db        Up 2 minutes        0.0.0.0:35432->5432/tcp
```

### API 테스트

```bash
# 헬스체크
curl http://localhost:38000/

# Swagger 접속
curl http://localhost:38000/docs

# 실제 분석 요청
curl -X POST http://localhost:38000/stock/analyze \
  -H "Content-Type: application/json" \
  -d '{"company": "TSLA"}'
```

---

## 📝 로그 확인

```bash
cd /root/stock-invest

# 전체 로그
docker-compose logs -f

# API 로그만
docker-compose logs -f stock-invest-api

# DB 로그만
docker-compose logs -f stock-invest-db

# 최근 100줄
docker-compose logs --tail=100
```

---

## 🛠️ 관리 명령어

### 시작/중지/재시작

```bash
cd /root/stock-invest

# 시작
docker-compose up -d

# 중지
docker-compose down

# 재시작
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart stock-invest-api
```

### 컨테이너 접속

```bash
# API 컨테이너
docker exec -it stock-invest-api bash

# DB 접속
docker exec -it stock-invest-db psql -U postgres -d stock_analysis
```

### DB 백업/복원

```bash
# 백업
docker exec stock-invest-db pg_dump -U postgres stock_analysis > backup-$(date +%Y%m%d).sql

# 복원
cat backup.sql | docker exec -i stock-invest-db psql -U postgres -d stock_analysis
```

---

## 🔒 보안 설정

### 1. DB 비밀번호 변경

```bash
# .env.prod 편집
nano .env.prod

# DB_PASSWORD 변경
DB_PASSWORD=your-very-secure-password
```

재배포:
```bash
docker-compose down -v  # 주의: 데이터 삭제됨!
docker-compose up -d
```

### 2. 방화벽 설정

```bash
# UFW (Ubuntu)
sudo ufw allow 38000/tcp
sudo ufw allow 35432/tcp

# firewalld (CentOS)
sudo firewall-cmd --permanent --add-port=38000/tcp
sudo firewall-cmd --permanent --add-port=35432/tcp
sudo firewall-cmd --reload
```

### 3. HTTPS 설정 (Nginx 리버스 프록시)

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:38000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🚨 트러블슈팅

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
sudo lsof -i :38000
sudo lsof -i :35432

# 프로세스 종료
sudo kill -9 <PID>
```

### 컨테이너가 시작 안됨

```bash
# 로그 확인
docker-compose logs stock-invest-api

# 재빌드
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### DB 연결 실패

```bash
# DB 상태 확인
docker-compose ps stock-invest-db

# DB 로그
docker-compose logs stock-invest-db

# 수동 연결 테스트
docker exec stock-invest-db pg_isready -U postgres
```

### 디스크 공간 부족

```bash
# Docker 정리
docker system prune -a

# 오래된 이미지 삭제
docker image prune -a
```

---

## 📈 모니터링

### 리소스 사용량

```bash
# 컨테이너 리소스 확인
docker stats

# 디스크 사용량
docker system df
```

### 자동 재시작 설정

이미 `restart: unless-stopped`로 설정되어 있습니다.

서버 재부팅 시 자동으로 컨테이너가 시작됩니다.

---

## 🔄 롤백

문제 발생 시 이전 버전으로 롤백:

```bash
cd /root/stock-invest

# 1. 이전 커밋으로 되돌리기
git log --oneline  # 커밋 해시 확인
git reset --hard <commit-hash>

# 2. 재배포
docker-compose down
docker-compose up -d --build
```

---

## 📊 배포 체크리스트

### 초기 배포

- [ ] Docker & Docker Compose 설치
- [ ] Git 설치
- [ ] 배포 스크립트 실행
- [ ] .env.prod API 키 설정
- [ ] DB 비밀번호 변경
- [ ] 방화벽 포트 열기
- [ ] API 동작 테스트
- [ ] 백업 스크립트 설정 (cron)

### 업데이트 시

- [ ] 데이터 백업
- [ ] update.sh 실행
- [ ] API 동작 확인
- [ ] 로그 확인

---

## 🎯 자동화 (Cron)

### 자동 업데이트 (매일 새벽 3시)

```bash
crontab -e

# 추가
0 3 * * * cd /root/stock-invest && ./update.sh >> /var/log/stock-invest-update.log 2>&1
```

### 자동 백업 (매일 새벽 2시)

```bash
crontab -e

# 추가
0 2 * * * docker exec stock-invest-db pg_dump -U postgres stock_analysis > /backups/stock-$(date +\%Y\%m\%d).sql
```

---

## 📞 문제 해결

문제 발생 시:

1. **로그 확인**: `docker-compose logs -f`
2. **상태 확인**: `docker-compose ps`
3. **재시작**: `docker-compose restart`
4. **재빌드**: `docker-compose down && docker-compose up -d --build`

---

## 🎉 배포 완료!

배포 후 접속:

- **API**: http://your-server:38000
- **Docs**: http://your-server:38000/docs

Happy Deploying! 🚀
