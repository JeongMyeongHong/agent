#!/bin/bash

# Production 환경 실행 스크립트

echo "🚀 Starting Stock Analysis API (Production Mode)"
echo "================================================"
echo "API Port: 38000"
echo "DB Port: 35432"
echo ""

# .env.prod 파일 존재 확인
if [ ! -f .env.prod ]; then
    echo "❌ Error: .env.prod file not found!"
    echo "Please create .env.prod from .env.example"
    exit 1
fi

# API 키 확인
if grep -q "your-openai-api-key-here" .env.prod; then
    echo "⚠️  Warning: OPENAI_API_KEY is not set in .env.prod"
fi

if grep -q "your-brave-api-key-here" .env.prod; then
    echo "⚠️  Warning: BRAVE_API_KEY is not set in .env.prod"
fi

echo "📦 Building Docker images..."
docker-compose --env-file .env.prod build

echo ""
echo "🏃 Starting services..."
docker-compose --env-file .env.prod up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Done!"
echo ""
echo "API URL: http://localhost:38000"
echo "API Docs: http://localhost:38000/docs"
echo "DB: localhost:35432"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop: docker-compose down"
