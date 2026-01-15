import FinanceDataReader as fdr

print("환경 설정 테스트 중...")
try:
    df = fdr.DataReader('005930', '2026-01-01')
    print("✅ 성공! 데이터 수집 완료:")
    print(df.tail(5))
except Exception as e:
    print(f"❌ 실패: {e}")
