# Python 3.13 베이스 이미지
FROM python:3.13-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (PostgreSQL 클라이언트 라이브러리)
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Node.js 및 npm 설치 (MCP Brave Search용)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# uv 설치 (Python 패키지 매니저)
RUN pip install --no-cache-dir uv

# 프로젝트 파일 복사
COPY pyproject.toml uv.lock* ./

# Python 의존성 설치
RUN uv pip install --system -r pyproject.toml

# 애플리케이션 코드 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 헬스체크 (선택사항)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# 애플리케이션 실행
CMD ["python", "main.py"]
