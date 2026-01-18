from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class StockRanking(BaseModel):
    Symbol: str
    Name: str
    MarketCap: Optional[int] = None  # 시가총액
    Close: float
    ChangeRate: Optional[float] = None  # 등락률

    class Config:
        from_attributes = True


# 상세 페이지 - 기업 정보
class TickerInfo(BaseModel):
    Symbol: str
    Name: str
    Sector: Optional[str] = None
    Industry: Optional[str] = None
    MarketCap: Optional[int] = None

    class Config:
        from_attributes = True


# 상세 페이지 - 주가 데이터
class StockData(BaseModel):
    Date: date
    Open: float
    Close: float
    Volume: int
    ChangeRate: Optional[float] = None
    MA_20: Optional[float] = None
    MA_50: Optional[float] = None
    MA_200: Optional[float] = None
    RSI_14: Optional[float] = None

    class Config:
        from_attributes = True


# 상세 페이지 - 통합 응답 (Info + Prices)
class StockDetailResponse(BaseModel):
    info: TickerInfo
    prices: List[StockData]
