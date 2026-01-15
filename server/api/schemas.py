from pydantic import BaseModel
from datetime import date
from typing import Optional


# API가 응답할 데이터의 형태
class StockData(BaseModel):
    Date: date
    Close: float
    MA_20: Optional[float] = None
    RSI_14: Optional[float] = None

    # 딕셔너리나 ORM 객체에서 데이터를 읽을 수 있게 설정
    class Config:
        from_attributes = True
