from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from server.core.database import get_db
from server.api.schemas import StockData, StockRanking
from typing import List

router = APIRouter()


# =========================================================================
# 1. 미국 시장 지수 조회 API
# =========================================================================
@router.get("/indices/major", response_model=List[StockRanking])
def get_major_indices(db: Session = Depends(get_db)):
    try:
        # 3개 지수를 한 번에 조회하고, 순서(다우 -> S&P -> 나스닥)로 정렬
        query = text("""
                     SELECT t.symbol      as "Symbol",
                            t.name        as "Name",
                            t.market_cap  as "MarketCap",
                            p.close       as "Close",
                            p.change_rate as "ChangeRate"
                     FROM tickers t
                              JOIN prices p ON t.symbol = p.ticker_symbol
                     WHERE t.symbol IN ('^GSPC', '^DJI', '^IXIC')
                       AND p.date = (SELECT MAX(date)
                                     FROM prices
                                     WHERE ticker_symbol = t.symbol)
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
                       AND p.date = (SELECT MAX(date)
                                     FROM prices
                                     WHERE ticker_symbol = t.symbol)
                     ORDER BY t.market_cap DESC NULLS LAST LIMIT :limit
                     """)

        result = db.execute(query, {"limit": limit})
        return result.mappings().all()

    except Exception as e:
        print(f"❌ [API Error] 랭킹 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류: 랭킹 조회 실패")


# =========================================================================
# 3. 특정 종목 상세 데이터 조회 API
# =========================================================================
@router.get("/stocks/{ticker}", response_model=List[StockData])
def get_stock_data(ticker: str, db: Session = Depends(get_db)):
    """
    [기능] 특정 종목의 1년치 주가 및 보조지표 조회
    [용도] 차트 및 상세 분석용
    """
    try:
        query = text("""
                     SELECT
                         date as "Date", open as "Open", close as "Close", volume as "Volume", change_rate as "ChangeRate", ma_20 as "MA_20", ma_50 as "MA_50", ma_200 as "MA_200", rsi_14 as "RSI_14"
                     FROM prices
                     WHERE ticker_symbol = :ticker
                     ORDER BY date DESC
                         LIMIT 365
                     """)

        result = db.execute(query, {"ticker": ticker})
        data = result.mappings().all()

        if not data:
            print(f"⚠️ [API Warning] 데이터 없음: {ticker}")
            return []

        return data

    except Exception as e:
        print(f"❌ [API Error] 상세 조회 실패 ({ticker}): {e}")
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {ticker}")
