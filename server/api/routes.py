from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from server.core.database import get_db
from server.api.schemas import StockData
from typing import List

router = APIRouter()


@router.get("/stocks/{ticker}", response_model=List[StockData])
def get_stock_data(ticker: str, db: Session = Depends(get_db)):
    """
    특정 종목의 데이터를 최신순으로 조회
    """
    try:
        # 날짜(Date) 기준으로 내림차순(최신순) 정렬하여 100개만 가져오기
        query = text(f"""
            SELECT index AS "Date", "Close", "MA_20", "RSI_14"
            FROM stock_prices
            ORDER BY "Date" DESC
            LIMIT 100
        """)

        result = db.execute(query)

        # DB 결과를 Pydantic 모델 리스트로 변환
        stocks = []
        for row in result:
            stocks.append(row._mapping)  # row를 딕셔너리처럼 변환

        return stocks

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="데이터 조회 중 오류 발생")
