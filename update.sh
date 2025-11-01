#!/bin/bash

# 업데이트 스크립트 (기존 배포를 최신 코드로 업데이트)

set -e

echo "🔄 Stock Investment API - Update Script"
echo "=========================================="
echo ""

DEPLOY_DIR="/root/stock-invest"

# 배포 디렉토리 확인
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "❌ Error: Deploy directory not found!"
    echo "   Please run deploy.sh first"
    exit 1
fi

cd "$DEPLOY_DIR"

echo "📥 Pulling latest code..."
git fetch origin
git reset --hard origin/main
git clean -fd

echo ""
echo "🛑 Stopping containers..."
docker-compose down

echo ""
echo "🔨 Building new images..."
docker-compose --env-file .env.prod build --no-cache

echo ""
echo "🚀 Starting containers..."
docker-compose --env-file .env.prod up -d

echo ""
echo "⏳ Waiting for services..."
sleep 10

echo ""
echo "✅ Update completed!"
echo ""
echo "📊 Current status:"
docker-compose ps

echo ""
echo "📝 View logs: docker-compose logs -f"
