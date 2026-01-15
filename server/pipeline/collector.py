import FinanceDataReader as fdr
import pandas as pd

from datetime import datetime, timedelta
from sqlalchemy import text
from server.core.database import engine


class StockCollector:
    def __init__(self, ticker: str = "NVDA"):
        self.ticker = ticker

    def fetch_data(self, days: int = 100) -> pd.DataFrame:
        # 오늘 날짜
        end_date = datetime.now().strftime('%Y-%m-%d')
        # 시작 날짜 (days + 60일 전부터 가져옴 - 이동평균선 계산용)
        start_date = (datetime.now() - timedelta(days=days + 60)).strftime('%Y-%m-%d')

        print(f"[{self.ticker}] 데이터를 수집하는 중입니다... ({start_date} ~ {end_date})")

        try:
            df = fdr.DataReader(self.ticker, start_date, end_date)

            if df.empty:
                print("데이터가 없습니다. 티커를 확인해주세요.")
                return pd.DataFrame()

            return df
        except Exception as e:
            print(f"수집 중 에러 발생: {e}")
            return pd.DataFrame()

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        수집된 데이터에 기술적 지표(이동평균선, RSI)를 추가
        """
        if df.empty:
            return df

        # 데이터 복사 (원본 보존)
        df = df.copy()

        # 1. 이동평균선 (Moving Average)
        df['MA_20'] = df['Close'].rolling(window=20).mean()  # 20일선 (단기 추세)
        df['MA_60'] = df['Close'].rolling(window=60).mean()  # 60일선 (중기 추세)

        # 2. RSI (상대강도지수) - 14일 기준
        delta = df['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

        rs = gain / loss
        df['RSI_14'] = 100 - (100 / (1 + rs))

        # 3. 전일 대비 변동률 (%)
        df['Change_Rate'] = df['Close'].pct_change() * 100

        # NaN(계산 불가능한 초기 데이터) 제거 및 소수점 정리
        df = df.dropna()
        df = df.round(2)

        return df

    def save_to_db(self, df: pd.DataFrame):
        """
        데이터프레임을 DB에 저장
        """
        if df.empty:
            print("저장할 데이터가 없습니다.")
            return

        table_name = "stock_prices"
        print(f"💾 [{self.ticker}] {len(df)}건의 데이터를 DB({table_name})에 저장합니다...")

        try:
            # if_exists='append': 테이블이 있으면 데이터 추가, 없으면 생성
            # index=True: 날짜 인덱스도 컬럼으로 같이 저장
            df.to_sql(name=table_name, con=engine, if_exists='append', index=True)
            print("✅ 저장 성공!")
        except Exception as e:
            print(f"❌ 저장 실패: {e}")

    def run(self):
        """
        수집 -> 가공 -> 저장
        """
        raw_df = self.fetch_data()
        processed_df = self.add_technical_indicators(raw_df)
        self.save_to_db(processed_df)
        return processed_df


if __name__ == "__main__":
    collector = StockCollector("NVDA")

    # 데이터 수집 및 가공
    result_df = collector.run()

    # 결과 출력
    print("\n" + "=" * 50)
    print(f"[{collector.ticker}] 최신 분석 데이터 (상위 5개)")
    print("=" * 50)
    # 최신 날짜순으로 보기 위해 역순 정렬 후 출력
    print(result_df.sort_index(ascending=False).head(5)[['Close', 'MA_20', 'RSI_14', 'Change_Rate']])
