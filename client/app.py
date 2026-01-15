import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="Ticker",
    page_icon="📈",
    layout="wide"
)

# 2. 제목 및 사이드바
st.title("📈 Ticker: 주식 데이터 분석 대시보드")
st.sidebar.header("검색 옵션")
ticker = st.sidebar.text_input("종목 코드 입력", value="NVDA")


# 3. API 서버에서 데이터 가져오기 함수
def fetch_stock_data(ticker_symbol):
    try:
        # FastAPI 서버 주소 (local)
        url = f"http://127.0.0.1:8000/api/v1/stocks/{ticker_symbol}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"데이터를 가져올 수 없습니다. (Status: {response.status_code})")
            return None
    except Exception as e:
        st.error(f"서버 연결 실패: {e}")
        return None


# 4. Main Logic
if st.button("조회하기") or ticker:
    data = fetch_stock_data(ticker)

    if data:
        # JSON -> DataFrame
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.set_index('Date')

        # 최신 데이터
        latest = df.iloc[0]
        prev = df.iloc[1]

        # --- 지표 카드 (Metric) 배치 ---
        col1, col2, col3 = st.columns(3)

        # 전일 대비 변동 계산
        diff = latest['Close'] - prev['Close']
        diff_pct = (diff / prev['Close']) * 100

        with col1:
            st.metric(label="현재 종가 (Close)",
                      value=f"${latest['Close']:.2f}",
                      delta=f"{diff:.2f} ({diff_pct:.2f}%)")
        with col2:
            st.metric(label="20일 이동평균 (MA20)",
                      value=f"${latest['MA_20']:.2f}")
        with col3:
            rsi = latest['RSI_14']
            state = "과매수 🔥" if rsi >= 70 else "과매도 🧊" if rsi <= 30 else "중립 😐"
            st.metric(label="RSI (14일)",
                      value=f"{rsi:.2f}",
                      delta=state, delta_color="off")

        st.divider()

        # --- 차트 그리기 ---
        st.subheader(f"📊 {ticker} 주가 추이 (최근 100일)")

        # 캔들차트 + 이동평균선
        fig = go.Figure()

        # 라인 차트 (종가)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['Close'],
            mode='lines', name='Close Price',
            line=dict(color='#00F0FF', width=2)
        ))

        # 라인 차트 (MA20)
        fig.add_trace(go.Scatter(
            x=df.index, y=df['MA_20'],
            mode='lines', name='MA 20',
            line=dict(color='#FFA500', width=1, dash='dot')
        ))

        fig.update_layout(
            template="plotly_dark",
            xaxis_title="날짜",
            yaxis_title="가격 (USD)",
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        with st.expander("💾 원본 데이터 보기"):
            st.dataframe(df)
