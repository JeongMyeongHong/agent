#!/bin/bash

# 자동 배포 스크립트
# GitHub에서 최신 코드를 받아서 Production 환경으로 배포

set -e  # 에러 발생 시 즉시 중단

echo "🚀 Stock Investment API - Auto Deploy Script"
echo "=============================================="
echo ""

# 설정
REPO_URL="https://github.com/JeongMyeongHong/agent.git"
DEPLOY_DIR="/root/stock-invest"  # 배포 디렉토리
API_DIR="$DEPLOY_DIR/api"  # API 소스 코드 디렉토리
BRANCH="main"  # 배포할 브랜치

# 현재 디렉토리 저장
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📍 설정 정보:"
echo "   Repository: $REPO_URL"
echo "   Deploy Directory: $DEPLOY_DIR"
echo "   API Directory: $API_DIR"
echo "   Branch: $BRANCH"
echo ""

# 1. 배포 디렉토리 생성
echo "📁 Step 1: 배포 디렉토리 준비..."
mkdir -p "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR/db"
echo "   ✅ Created deployment directories"

# 2. Git Clone 또는 Pull (api 디렉토리에)
echo ""
echo "📥 Step 2: 최신 코드 다운로드..."
if [ -d "$API_DIR/.git" ]; then
    echo "   Pulling latest changes..."
    cd "$API_DIR"
    git fetch origin
    git reset --hard origin/$BRANCH
    git clean -fd
else
    echo "   Cloning repository..."

    # api 디렉토리가 존재하지만 Git 저장소가 아닌 경우
    if [ -d "$API_DIR" ]; then
        echo "   Warning: $API_DIR exists but is not a git repository"
        echo "   Removing existing directory..."
        rm -rf "$API_DIR"
    fi

    # api 디렉토리에 clone
    git clone -b $BRANCH "$REPO_URL" "$API_DIR"
    cd "$API_DIR"
fi

# 3. docker-compose.yml을 프로젝트 루트로 복사
echo ""
echo "📋 Step 3: Docker Compose 설정..."
cp "$API_DIR/docker-compose.yml" "$DEPLOY_DIR/"
echo "   ✅ Copied docker-compose.yml to $DEPLOY_DIR"

# 4. 기존 컨테이너 중지 (있다면)
echo ""
echo "🛑 Step 4: 기존 컨테이너 중지..."
cd "$DEPLOY_DIR"
if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo "   Stopping existing containers..."
    docker-compose down 2>/dev/null || echo "   Failed to stop containers"
else
    echo "   No running containers found"
fi

# 5. 환경 변수 파일 확인
echo ""
echo "🔑 Step 5: 환경 변수 확인..."
cd "$DEPLOY_DIR"
if [ ! -f ".env.prod" ]; then
    echo "   ⚠️  Warning: .env.prod not found!"
    echo "   Creating from .env.example..."
    if [ -f "$API_DIR/.env.example" ]; then
        cp "$API_DIR/.env.example" .env.prod
        echo ""
        echo "   ❗ IMPORTANT: Please edit .env.prod with your API keys!"
        echo "   File location: $DEPLOY_DIR/.env.prod"
        echo ""
        read -p "   Press Enter to continue or Ctrl+C to exit..."
    else
        echo "   ❌ Error: .env.example not found!"
        exit 1
    fi
else
    echo "   ✅ .env.prod found"
fi

# API 키 확인
if grep -q "your-openai-api-key-here" .env.prod; then
    echo "   ⚠️  Warning: OPENAI_API_KEY is not configured!"
fi

if grep -q "your-brave-api-key-here" .env.prod; then
    echo "   ⚠️  Warning: BRAVE_API_KEY is not configured!"
fi

# 6. Docker 이미지 빌드
echo ""
echo "🔨 Step 6: Docker 이미지 빌드..."
docker-compose --env-file .env.prod build --no-cache

# 7. 컨테이너 시작
echo ""
echo "🚀 Step 7: 컨테이너 시작..."
docker-compose --env-file .env.prod up -d

# 8. 헬스체크
echo ""
echo "⏳ Step 8: 서비스 헬스체크 (30초 대기)..."
sleep 10

# DB 헬스체크
echo "   Checking database..."
for i in {1..10}; do
    if docker exec stock-invest-db pg_isready -U postgres >/dev/null 2>&1; then
        echo "   ✅ Database is ready"
        break
    fi
    echo "   Waiting for database... ($i/10)"
    sleep 2
done

# API 헬스체크
echo "   Checking API..."
sleep 5
for i in {1..10}; do
    if curl -f http://localhost:38000/ >/dev/null 2>&1; then
        echo "   ✅ API is ready"
        break
    fi
    echo "   Waiting for API... ($i/10)"
    sleep 2
done

# 9. 최종 상태 확인
echo ""
echo "📊 Step 9: 배포 상태 확인..."
docker-compose ps

# 10. 배포 완료
echo ""
echo "✅ 배포 완료!"
echo "=============================================="
echo ""
echo "📍 접속 정보:"
echo "   API URL:  http://localhost:38000"
echo "   API Docs: http://localhost:38000/docs"
echo "   DB Port:  localhost:35432"
echo ""
echo "📝 유용한 명령어:"
echo "   로그 확인:     cd $DEPLOY_DIR && docker-compose logs -f"
echo "   재시작:        cd $DEPLOY_DIR && docker-compose restart"
echo "   중지:          cd $DEPLOY_DIR && docker-compose down"
echo "   상태 확인:     cd $DEPLOY_DIR && docker-compose ps"
echo ""
echo "🎉 Happy Investing!"
