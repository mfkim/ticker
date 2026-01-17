from sqlalchemy import Column, String, Float, Date, BigInteger, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Ticker(Base):
    """
    종목 메타 정보
    - 변하지 않거나 드물게 변하는 정보 (회사명, 섹터, 산업군, 시가총액)
    """
    __tablename__ = "tickers"

    # 기본 정보
    symbol = Column(String(10), primary_key=True, index=True)
    name = Column(String(150))  # 회사명
    sector = Column(String(100))  # 섹터
    industry = Column(String(150))  # 산업군

    # 펀더멘탈 & 관리
    market_cap = Column(BigInteger, nullable=True)  # 시가총액
    is_active = Column(Boolean, default=True)  # S&P 500 포함 여부

    # 관계 설정 (1:N)
    prices = relationship("Price", back_populates="ticker", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Ticker(symbol='{self.symbol}', name='{self.name}', cap={self.market_cap})>"


class Price(Base):
    """
    [Transaction Table] 일별 주가 및 기술적 지표
    - 매일 쌓이는 시계열 데이터
    """
    __tablename__ = "prices"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 외래 키 (Ticker 테이블과 연결)
    ticker_symbol = Column(String(10), ForeignKey("tickers.symbol"), index=True)
    date = Column(Date, index=True)

    # OHLCV (기본 주가 데이터)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    # 분석 지표 (수집 단계에서 미리 계산하여 저장)
    change_rate = Column(Float)  # 등락률 (%) -> 전광판 색상 결정
    ma_20 = Column(Float, nullable=True)  # 20일 이동평균 (단기)
    ma_50 = Column(Float, nullable=True)  # 50일 이동평균 (중기)
    ma_200 = Column(Float, nullable=True)  # 200일 이동평균 (장기 - 경기선)
    rsi_14 = Column(Float, nullable=True)  # RSI (과매수/과매도 판단)

    # 관계 설정
    ticker = relationship("Ticker", back_populates="prices")

    # 복합 인덱스 & 유니크 제약
    # 한 종목에 같은 날짜 데이터가 중복해서 들어가는 것을 DB 차원에서 방지
    __table_args__ = (
        Index('idx_ticker_date', 'ticker_symbol', 'date', unique=True),
    )

    def __repr__(self):
        return f"<Price(ticker='{self.ticker_symbol}', date='{self.date}', close={self.close})>"
