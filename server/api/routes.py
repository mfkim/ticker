from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from server.core.database import get_db
from server.api.schemas import StockData, StockRanking
from typing import List

router = APIRouter()


# =========================================================================
# 1. 시가총액별 랭킹 조회 API (Top N)
# =========================================================================
@router.get("/stocks/ranking", response_model=List[StockRanking])
def get_stock_ranking(limit: int = 100, db: Session = Depends(get_db)):
    """
    [기능] S&P 500 종목을 시가총액(Market Cap) 순으로 정렬하여 반환
    [설명] 각 종목의 가장 최신 날짜(Latest Date) 데이터를 조회
    """
    try:
        # Pydantic 필드명(PascalCase)에 맞춰 별칭(AS) 지정
        query = text("""
                     SELECT t.symbol      as "Symbol",
                            t.name        as "Name",
                            t.market_cap  as "MarketCap",
                            p.close       as "Close",
                            p.change_rate as "ChangeRate"
                     FROM tickers t
                              JOIN prices p ON t.symbol = p.ticker_symbol
                     WHERE t.is_active = true
                       AND p.date = (
                         -- 각 종목별 가장 최신 날짜의 데이터만 선택
                         SELECT MAX(date)
                         FROM prices
                         WHERE ticker_symbol = t.symbol)
                     ORDER BY t.market_cap DESC NULLS LAST LIMIT :limit
                     """)

        result = db.execute(query, {"limit": limit})

        # 최신 SQLAlchemy 방식: 결과를 딕셔너리 형태로 변환
        return result.mappings().all()

    except Exception as e:
        print(f"❌ [API Error] 랭킹 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="서버 내부 오류: 랭킹 조회 실패")


# =========================================================================
# 2. 특정 종목 상세 데이터 조회 API
# =========================================================================
@router.get("/stocks/{ticker}", response_model=List[StockData])
def get_stock_data(ticker: str, db: Session = Depends(get_db)):
    """
    [기능] 특정 종목의 1년치 주가 및 보조지표 조회
    [용도] 상세 페이지의 차트 및 메트릭 표시에 사용
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
            # 데이터가 없으면 빈 리스트 반환
            return []

        return data

    except Exception as e:
        print(f"❌ [API Error] 상세 조회 실패 ({ticker}): {e}")
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {ticker}")
