from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from server.core.database import get_db
from server.api.schemas import StockData, StockRanking, StockDetailResponse, TickerInfo
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
@router.get("/stocks/{ticker}", response_model=StockDetailResponse)
def get_stock_data(ticker: str, db: Session = Depends(get_db)):
    """
    [기능] 특정 종목의 기업 정보와 1년치 주가를 한 번에 조회
    """
    try:
        # 1. 기업 정보 조회 (Tickers 테이블)
        # 쿼리 결과 컬럼명을 Pydantic 모델(TickerInfo)과 일치시킴
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

        # 2. 주가 데이터 조회 (Prices 테이블)
        price_query = text("""
                           SELECT
                               date as "Date", open as "Open", close as "Close", volume as "Volume", change_rate as "ChangeRate", ma_20 as "MA_20", ma_50 as "MA_50", ma_200 as "MA_200", rsi_14 as "RSI_14"
                           FROM prices
                           WHERE ticker_symbol = :ticker
                           ORDER BY date DESC
                               LIMIT 365
                           """)
        price_result = db.execute(price_query, {"ticker": ticker}).mappings().all()

        # 3. 통합 반환
        return {
            "info": info_result,
            "prices": price_result
        }

    except Exception as e:
        print(f"❌ [API Error] 상세 조회 실패 ({ticker}): {e}")
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {ticker}")
