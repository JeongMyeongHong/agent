from contextlib import asynccontextmanager
from fastapi import FastAPI
from api import router as stock_router
from database import init_db


@asynccontextmanager
async def lifespan(_):
    """애플리케이션 라이프사이클 관리"""
    # Startup
    try:
        init_db()
        print("[APP] 애플리케이션 시작 완료 - DB 연결 성공")
    except Exception as e:
        print(f"[APP] 데이터베이스 초기화 실패: {e}")
        print("[APP] 계속 진행하지만 캐시 기능은 비활성화됩니다.")

    yield

    # Shutdown (필요한 경우 정리 작업 추가)
    print("[APP] 애플리케이션 종료")


app = FastAPI(
    title="Stock Analysis API",
    version="1.0.0",
    description="OpenAI GPT-5를 사용한 주식 종합 분석 API",
    lifespan=lifespan,
)

# 라우터 등록
app.include_router(stock_router)


@app.get("/")
async def root():
    return {
        "message": "Stock Analysis API is running",
        "version": "1.0.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False, workers=3)
