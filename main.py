from fastapi import FastAPI
from api import router as stock_router

app = FastAPI(
    title="Stock Analysis API",
    version="1.0.0",
    description="OpenAI GPT-5를 사용한 주식 종합 분석 API",
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
