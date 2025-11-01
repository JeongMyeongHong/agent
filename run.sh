#!/bin/bash

# 간단한 로컬 실행 스크립트

# .env.local을 .env로 복사
cp .env.local .env 2>/dev/null || echo "Using existing .env"

# Python 실행
echo "🚀 Starting API on http://localhost:8000"
python main.py
