#!/bin/bash

# Local 환경 실행 스크립트 (외부 DB 사용)

echo "🏠 Starting Stock Analysis API (Local Mode)"
echo "============================================"
echo "API Port: 38000"
echo "DB: 175.117.82.131:5432 (External)"
echo ""

# .env.local 파일 존재 확인
if [ ! -f .env.local ]; then
    echo "❌ Error: .env.local file not found!"
    echo "Please create .env.local from .env.example"
    exit 1
fi

# API 키 확인
if grep -q "your-openai-api-key-here" .env.local; then
    echo "⚠️  Warning: OPENAI_API_KEY is not set in .env.local"
fi

if grep -q "your-brave-api-key-here" .env.local; then
    echo "⚠️  Warning: BRAVE_API_KEY is not set in .env.local"
fi

# 외부 DB 연결 테스트
echo "🔌 Testing connection to external DB..."
if command -v nc &> /dev/null; then
    if nc -z 175.117.82.131 5432 2>/dev/null; then
        echo "✅ DB connection OK"
    else
        echo "⚠️  Warning: Cannot connect to 175.117.82.131:5432"
        echo "Please check if the database is running and accessible"
    fi
else
    echo "⚠️  'nc' command not found, skipping DB connection test"
fi

echo ""
echo "📦 Building Docker image..."
docker-compose -f docker-compose.local.yml --env-file .env.local build

echo ""
echo "🏃 Starting API service..."
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

echo ""
echo "⏳ Waiting for service to be ready..."
sleep 3

echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.local.yml ps

echo ""
echo "✅ Done!"
echo ""
echo "API URL: http://localhost:38000"
echo "API Docs: http://localhost:38000/docs"
echo ""
echo "View logs: docker-compose -f docker-compose.local.yml logs -f"
echo "Stop: docker-compose -f docker-compose.local.yml down"
