import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Ticker", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* 전체 배경 */
    .stApp { background-color: #0E1117; }

    /* 헤더 */
    h1 { color: white; font-weight: 800; letter-spacing: -1px; margin-bottom: 0px; }
    .caption { color: #888; font-size: 16px; margin-bottom: 30px; }

    /* 카드 컨테이너 */
    .stock-card {
        background-color: #1A1A1A;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        transition: transform 0.2s, border-color 0.2s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }

    /* 호버 효과 */
    .stock-card:hover {
        transform: translateY(-3px);
        border-color: #555;
        box-shadow: 0 8px 15px rgba(0,0,0,0.3);
    }

    /* 텍스트 */
    .symbol { font-size: 20px; font-weight: 800; color: #FFFFFF; display: flex; justify-content: space-between; align-items: center; }
    .name { font-size: 13px; color: #888; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 4px; margin-bottom: 12px; }
    .price-row { display: flex; justify-content: space-between; align-items: flex-end; }
    .price { font-size: 24px; font-weight: 700; color: #EEEEEE; }

    /* 등락률 배지 */
    .badge {
        font-size: 14px;
        font-weight: 700;
        padding: 4px 8px;
        border-radius: 6px;
    }
    .up-bg { background-color: rgba(0, 200, 5, 0.15); color: #00FF41; border: 1px solid rgba(0, 200, 5, 0.3); }
    .down-bg { background-color: rgba(255, 80, 0, 0.15); color: #FF5000; border: 1px solid rgba(255, 80, 0, 0.3); }

    /* 기본 여백 제거 */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
</style>
""", unsafe_allow_html=True)


# API
@st.cache_data(ttl=60)
def fetch_ranking(limit=100):
    try:
        url = f"http://127.0.0.1:8000/api/v1/stocks/ranking?limit={limit}"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            return pd.DataFrame(resp.json())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()


st.title("S&P 500")
st.markdown("<div class='caption'>Top 100 Companies by Market Capitalization</div>",
            unsafe_allow_html=True)

df = fetch_ranking(limit=100)

if not df.empty:
    cols_per_row = 5
    rows = [st.columns(cols_per_row) for _ in range((len(df) // cols_per_row) + 1)]

    for index, row in df.iterrows():
        col_idx = index % cols_per_row
        row_idx = index // cols_per_row
        current_col = rows[row_idx][col_idx]

        with current_col:
            symbol = row['Symbol']
            name = row['Name']
            price = row['Close']
            pct = row['ChangeRate'] if pd.notnull(row['ChangeRate']) else 0.0

            if pct >= 0:
                badge_class = "up-bg"
                sign = "+"
            else:
                badge_class = "down-bg"
                sign = ""

            st.markdown(f"""
            <div class="stock-card">
                <div class="symbol">
                    {symbol}
                </div>
                <div class="name" title="{name}">{name}</div>
                <div class="price-row">
                    <div class="price">${price:,.2f}</div>
                    <div class="badge {badge_class}">
                        {sign}{pct:.2f}%
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.error("⚠️ 서버 연결 실패. 서버가 실행 중인지 확인해주세요.")
