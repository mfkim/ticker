import pandas as pd
from prophet import Prophet
from sqlalchemy.orm import Session
from sqlalchemy import text


def run_prediction(symbol: str, db: Session, days: int = 30):
    """
    Prophet 모델을 사용하여 향후 N일간의 주가 예측
    """
    # 1. DB에서 과거 데이터 가져오기
    query = text("""
                 SELECT date as ds, close as y
                 FROM prices
                 WHERE ticker_symbol = :symbol
                 ORDER BY date ASC
                 """)
    result = db.execute(query, {"symbol": symbol}).mappings().all()

    if not result or len(result) < 30:
        return None  # 데이터가 너무 적으면 예측 불가

    # 2. DataFrame 변환
    df = pd.DataFrame(result)

    # 3. Prophet 모델 학습
    # daily_seasonality=True: 일일 변동성 반영
    # changepoint_prior_scale: 트렌드 변화 민감도
    model = Prophet(daily_seasonality=True, changepoint_prior_scale=0.05)
    model.fit(df)

    # 4. 미래 날짜 데이터프레임 생성
    future = model.make_future_dataframe(periods=days)

    # 5. 예측 실행
    forecast = model.predict(future)

    # 6. 결과 정리 (마지막 N일치만 추출)
    # ds: 날짜, yhat: 예측값, yhat_lower: 최저 예상, yhat_upper: 최고 예상
    prediction_data = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)

    # JSON 직렬화를 위해 날짜를 문자열로 변환
    prediction_result = []
    for _, row in prediction_data.iterrows():
        prediction_result.append({
            "Date": row['ds'].strftime('%Y-%m-%d'),
            "PredictedClose": round(row['yhat'], 2),
            "LowerBound": round(row['yhat_lower'], 2),
            "UpperBound": round(row['yhat_upper'], 2)
        })

    return prediction_result
