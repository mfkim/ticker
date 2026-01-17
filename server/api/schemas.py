from pydantic import BaseModel
from datetime import date
from typing import Optional, List


# ---------------------------------------------------------
# 랭킹 리스트
# ---------------------------------------------------------
class StockRanking(BaseModel):
    Symbol: str
    Name: str
    MarketCap: Optional[int] = None  # 시가총액 (Top 100 정렬 기준)
    Close: float
    ChangeRate: Optional[float] = None  # 등락률 (색상 결정)

    class Config:
        from_attributes = True


# ---------------------------------------------------------
# 상세 조회
# ---------------------------------------------------------
class StockData(BaseModel):
    Date: date
    Open: float
    Close: float
    Volume: int
    ChangeRate: Optional[float] = None

    # 기술적 지표 (Collector가 미리 계산)
    MA_20: Optional[float] = None
    MA_50: Optional[float] = None
    MA_200: Optional[float] = None
    RSI_14: Optional[float] = None

    class Config:
        from_attributes = True
