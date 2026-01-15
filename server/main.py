from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.api.routes import router as stock_router

app = FastAPI(
    title="Ticker API",
    description="주식 데이터 분석 및 제공 API",
    version="0.0.1"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(stock_router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"message": "Welcome to Ticker API Server! 🚀"}
