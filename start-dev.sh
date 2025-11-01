#!/bin/bash

# 로컬 개발 환경 실행 (Docker 없이)

echo "💻 Starting Stock Analysis API (Development Mode)"
echo "================================================="
echo "Running directly on host (no Docker)"
echo "API Port: 8000"
echo "DB: 175.117.82.131:5432 (External)"
echo ""

# .env.local 파일을 .env로 복사 (또는 심볼릭 링크)
if [ -f .env.local ]; then
    echo "📝 Using .env.local configuration..."
    cp .env.local .env
else
    echo "❌ Error: .env.local file not found!"
    echo "Please create .env.local from .env.example"
    exit 1
fi

# Python 가상환경 확인
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv .venv
fi

# 가상환경 활성화
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# 의존성 설치 확인
echo "📦 Installing dependencies..."
if command -v uv &> /dev/null; then
    echo "Using uv..."
    uv pip install -e .
else
    echo "Using pip..."
    pip install -e .
fi

# Node.js 및 npm 확인 (MCP용)
if ! command -v node &> /dev/null; then
    echo "⚠️  Warning: Node.js is not installed!"
    echo "MCP Brave Search will not work without Node.js"
    echo "Install: brew install node"
fi

# 외부 DB 연결 테스트
echo ""
echo "🔌 Testing connection to external DB..."
if command -v nc &> /dev/null; then
    if nc -z 175.117.82.131 5432 2>/dev/null; then
        echo "✅ DB connection OK"
    else
        echo "⚠️  Warning: Cannot connect to 175.117.82.131:5432"
        echo "Please check if the database is running and accessible"
    fi
else
    if command -v telnet &> /dev/null; then
        timeout 2 telnet 175.117.82.131 5432 2>/dev/null && echo "✅ DB connection OK" || echo "⚠️  Warning: Cannot connect to DB"
    fi
fi

echo ""
echo "🚀 Starting application..."
echo "Press Ctrl+C to stop"
echo ""

# 애플리케이션 실행
python main.py
