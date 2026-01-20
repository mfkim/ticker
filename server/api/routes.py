from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

# DB 및 스키마
from server.core.database import get_db
from server.api.schemas import (
    StockData,
    StockRanking,
    StockDetailResponse,
    TickerInfo,
    PredictionData
)

# AI 예측 서비스
from server.services.predictor import run_prediction

router = APIRouter()


# =========================================================================
# 1. 미국 시장 지수 조회 API
# =========================================================================
@router.get("/indices/major", response_model=List[StockRanking])
def get_major_indices(db: Session = Depends(get_db)):
    """
    [기능] 미국 3대 지수(^GSPC, ^DJI, ^IXIC)의 최신 현황 조회
    """
    try:
        query = text("""
                     SELECT t.symbol      as "Symbol",
                            t.name        as "Name",
                            t.market_cap  as "MarketCap",
                            p.close       as "Close",
                            p.change_rate as "ChangeRate"
                     FROM tickers t
                              JOIN prices p ON t.symbol = p.ticker_symbol
                     WHERE t.symbol IN ('^GSPC', '^DJI', '^IXIC')
                       AND p.date = (SELECT MAX(date) FROM prices WHERE ticker_symbol = t.symbol)
                     ORDER BY CASE t.symbol
                                  WHEN '^DJI' THEN 1
                                  WHEN '^GSPC' THEN 2
                                  WHEN '^IXIC' THEN 3
                                  END
                     """)

        result = db.execute(query)
        return result.mappings().all()

    except Exception as e:
        print(f"❌ [API Error] 지수 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류: 지수 데이터 조회 실패")


# =========================================================================
# 2. 시가총액별 랭킹 조회 API (Top N)
# =========================================================================
@router.get("/stocks/ranking", response_model=List[StockRanking])
def get_stock_ranking(limit: int = 100, db: Session = Depends(get_db)):
    """
    [기능] S&P 500 종목을 시가총액(Market Cap) 순으로 정렬하여 반환
    [설명] 지수(Index)는 제외하고, 활성화된(is_active=True) 종목만 조회
    """
    try:
        query = text("""
                     SELECT t.symbol      as "Symbol",
                            t.name        as "Name",
                            t.market_cap  as "MarketCap",
                            p.close       as "Close",
                            p.change_rate as "ChangeRate"
                     FROM tickers t
                              JOIN prices p ON t.symbol = p.ticker_symbol
                     WHERE t.is_active = true
                       AND p.date = (SELECT MAX(date) FROM prices WHERE ticker_symbol = t.symbol)
                     ORDER BY t.market_cap DESC NULLS LAST LIMIT :limit
                     """)

        result = db.execute(query, {"limit": limit})
        return result.mappings().all()

    except Exception as e:
        print(f"❌ [API Error] 랭킹 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류: 랭킹 조회 실패")


# =========================================================================
# 3. 특정 종목 상세 데이터 조회 API (기업정보 + 주가)
# =========================================================================
@router.get("/stocks/{ticker}", response_model=StockDetailResponse)
def get_stock_data(ticker: str, db: Session = Depends(get_db)):
    """
    [기능] 특정 종목의 기업 정보와 1년치 주가를 한 번에 조회
    """
    try:
        # 1. 기업 정보 조회
        info_query = text("""
                          SELECT symbol     as "Symbol",
                                 name       as "Name",
                                 sector     as "Sector",
                                 industry   as "Industry",
                                 market_cap as "MarketCap"
                          FROM tickers
                          WHERE symbol = :ticker
                          """)
        info_result = db.execute(info_query, {"ticker": ticker}).mappings().first()

        if not info_result:
            raise HTTPException(status_code=404, detail="종목 정보를 찾을 수 없습니다.")

        # 2. 주가 데이터 조회 (1년치)
        price_query = text("""
                           SELECT
                               date as "Date", open as "Open", close as "Close", volume as "Volume", change_rate as "ChangeRate", ma_20 as "MA_20", ma_50 as "MA_50", ma_200 as "MA_200", rsi_14 as "RSI_14"
                           FROM prices
                           WHERE ticker_symbol = :ticker
                           ORDER BY date DESC
                               LIMIT 365
                           """)
        price_result = db.execute(price_query, {"ticker": ticker}).mappings().all()

        return {
            "info": info_result,
            "prices": price_result
        }

    except Exception as e:
        print(f"❌ [API Error] 상세 조회 실패 ({ticker}): {e}")
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {ticker}")


# =========================================================================
# 4. 주가 예측 API
# =========================================================================
@router.get("/stocks/{ticker}/predict", response_model=List[PredictionData])
def predict_stock(ticker: str, days: int = 30, db: Session = Depends(get_db)):
    """
    [기능] Prophet AI 모델을 실행하여 향후 N일간의 주가를 예측
    [참고] 실시간 연산으로 인해 응답에 수 초가 소요될 수 있음
    """
    try:
        print(f"🤖 AI Forecasting started for: {ticker}")

        # 서비스 계층의 예측 함수 호출
        predictions = run_prediction(ticker, db, days)

        if not predictions:
            raise HTTPException(status_code=400, detail="예측을 위한 데이터가 부족합니다 (최소 30일 필요).")

        return predictions

    except Exception as e:
        print(f"❌ [Prediction Error]: {e}")
        raise HTTPException(status_code=500, detail=f"AI 예측 실패: {str(e)}")
