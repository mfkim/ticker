import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker, scoped_session
from server.core.database import engine, init_db
from server.core.models import Ticker, Price

# 전역 세션 팩토리 생성 (스레드 안전성 확보)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class StockCollector:
    """
    S&P 500 주가 데이터 수집 및 관리 파이프라인
    - Ticker 동기화: yfinance
    - Price 수집: FinanceDataReader
    """

    def __init__(self):
        self.ticker_exceptions = {
            'BRKB': 'BRK-B',
            'BFB': 'BF-B'
        }

    def _get_session(self):
        """DB 세션 생성 (Context Management)"""
        return Session()

    def sync_metadata(self):
        """
        1. 종목 메타데이터 동기화
        - S&P 500 리스트를 가져오고, yfinance를 통해 정확한 시가총액을 업데이트
        """
        print("\n" + "=" * 50)
        print("📋 Phase 1: 종목 메타데이터(시가총액) 동기화 시작")
        print("=" * 50)

        session = self._get_session()

        try:
            df_sp500 = fdr.StockListing('S&P500')
            sp500_symbols = df_sp500['Symbol'].tolist()
            total_count = len(sp500_symbols)

            print(f"✅ S&P 500 종목 리스트 확보 완료: {total_count}개")
            print("⏳ yfinance를 통한 상세 정보 스캔 중 (약 2~3분 소요)...")

            updated_count = 0

            for i, symbol in enumerate(sp500_symbols):
                # 진행률 표시
                if i % 10 == 0:
                    print(f"   Processing... {i + 1}/{total_count}", end='\r')

                yf_symbol = self.ticker_exceptions.get(symbol, symbol)

                try:
                    # yfinance로 상세 정보 조회
                    # Ticker 객체 생성 시 네트워크 요청은 발생하지 않음
                    ticker_dat = yf.Ticker(yf_symbol)

                    # .info 접근 시 실제 API 호출 발생
                    info = ticker_dat.info

                    # 데이터 추출 (없으면 None 또는 Unknown)
                    market_cap = info.get('marketCap')
                    sector = info.get('sector', 'Unknown')
                    industry = info.get('industry', 'Unknown')
                    name = info.get('shortName', info.get('longName', symbol))

                    # DB 객체 생성 및 Upsert (Merge)
                    ticker_obj = Ticker(
                        symbol=symbol,
                        name=name,
                        sector=sector,
                        industry=industry,
                        market_cap=market_cap,
                        is_active=True
                    )
                    session.merge(ticker_obj)

                    if market_cap:
                        updated_count += 1

                except Exception as e:
                    # 개별 종목 실패는 로그만 남기고 계속 진행
                    # print(f"   ⚠️ [{symbol}] 메타 정보 수집 실패: {e}")
                    pass

            session.commit()
            print(f"\n✅ 메타데이터 동기화 완료! (시가총액 확보: {updated_count}/{total_count}개)")

            return sp500_symbols

        except Exception as e:
            session.rollback()
            print(f"\n❌ 치명적 오류 발생: {e}")
            return []
        finally:
            session.close()

    def process_prices(self, symbol, days=365 * 2):
        """
        2. 개별 종목 주가 데이터 수집 및 가공
        """
        session = self._get_session()
        search_symbol = self.ticker_exceptions.get(symbol, symbol)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        try:
            # 1. 기존 데이터 삭제 (Clean Insert)
            # 중복 에러를 방지하고 데이터 무결성을 위해 해당 종목의 데이터를 지우고 다시 씀
            session.query(Price).filter(Price.ticker_symbol == symbol).delete()

            # 2. 데이터 다운로드
            df = fdr.DataReader(search_symbol, start_date, end_date)
            if df.empty:
                session.commit()  # 삭제 내역만 커밋하고 종료
                return

            # 3. 기술적 지표 계산 (Pandas Vectorization)
            # 등락률 (FutureWarning 해결: fill_method=None)
            df['change_rate'] = df['Close'].pct_change(fill_method=None) * 100

            # 이동평균선
            df['ma_20'] = df['Close'].rolling(window=20).mean()
            df['ma_50'] = df['Close'].rolling(window=50).mean()
            df['ma_200'] = df['Close'].rolling(window=200).mean()

            # RSI (14)
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi_14'] = 100 - (100 / (1 + rs))

            # NaN 제거 (지표 계산 초반 구간)
            df = df.dropna()

            # 4. Bulk Insert용 객체 리스트 생성
            prices_to_add = []
            for index, row in df.iterrows():
                prices_to_add.append(Price(
                    ticker_symbol=symbol,
                    date=index.date(),
                    open=float(row['Open']),
                    high=float(row['High']),
                    low=float(row['Low']),
                    close=float(row['Close']),
                    volume=int(row['Volume']),
                    change_rate=float(row['change_rate']),
                    ma_20=float(row['ma_20']),
                    ma_50=float(row['ma_50']),
                    ma_200=float(row['ma_200']),
                    rsi_14=float(row['rsi_14'])
                ))

            session.add_all(prices_to_add)
            session.commit()
            # print(f"💾 [{symbol}] 데이터 갱신 완료 ({len(prices_to_add)}일)")

        except Exception as e:
            session.rollback()
            print(f"❌ [{symbol}] 가격 수집 실패: {e}")
        finally:
            session.close()

    def run(self, limit=None):
        """
        전체 파이프라인 실행 함수
        """
        print("🚀 Stock Collector Pipeline Started...")

        # 1. DB 테이블 초기화 (없으면 생성)
        init_db()

        # 2. 종목 정보 동기화
        symbols = self.sync_metadata()

        # ---------------------------------------------------------
        # 📊 Phase 1.5: 미국 시장 지수 수집 (S&P500, Dow, Nasdaq)
        # ---------------------------------------------------------
        print("\n" + "=" * 50)
        print("📊 Phase 1.5: 주요 시장 지수(Indices) 수집")
        print("=" * 50)

        # 수집할 지수 목록 정의
        TARGET_INDICES = [
            {'symbol': '^GSPC', 'name': 'S&P 500'},
            {'symbol': '^DJI', 'name': 'Dow Jones 30'},
            {'symbol': '^IXIC', 'name': 'NASDAQ Composite'}
        ]

        session = self._get_session()
        try:
            for idx in TARGET_INDICES:
                symbol = idx['symbol']
                name = idx['name']

                # 지수용 Ticker 생성/업데이트
                idx_ticker = Ticker(
                    symbol=symbol,
                    name=name,
                    sector="Index",
                    industry="Market",
                    market_cap=0,
                    is_active=False
                )
                session.merge(idx_ticker)
                session.commit()

                # 주가 수집 실행
                print(f"   Processing Index: {name} ({symbol})...", end='\r', flush=True)
                self.process_prices(symbol)
                print(f"✅ 지수 수집 완료: {name:<20}       ")

        except Exception as e:
            print(f"❌ 지수 수집 실패: {e}")
        finally:
            session.close()

        if not symbols:
            print("❌ 종목 리스트를 가져오지 못해 종료합니다.")
            return

        # 수집 대상 설정
        target_symbols = symbols[:limit] if limit else symbols
        total = len(target_symbols)

        print("\n" + "=" * 50)
        print(f"💾 Phase 2: 주가 데이터 수집 시작 (대상: {total}개)")
        print("=" * 50)

        # 3. 주가 수집 루프
        start_time = time.time()
        for i, symbol in enumerate(target_symbols):
            # 진행률 바 표시
            progress = (i + 1) / total * 100
            elapsed = time.time() - start_time
            print(f"[{i + 1}/{total}] {symbol:<5} |{'█' * int(progress / 2):<50}| {progress:.1f}% ({elapsed:.1f}s)",
                  end='\r', flush=True)

            self.process_prices(symbol)
            # API 과부하 방지
            time.sleep(0.1)

        print(f"\n\n✅ 모든 수집 작업이 완료되었습니다! (총 소요시간: {time.time() - start_time:.1f}초)")


if __name__ == "__main__":
    collector = StockCollector()

    collector.run(limit=1)
