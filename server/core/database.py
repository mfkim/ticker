from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 1. 환경변수 설정
# 실제 배포 시에는 보안을 위해 환경변수로 주입
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/ticker_db")

# 2. 엔진 생성 (안정성 옵션 추가)
engine = create_engine(
    DATABASE_URL,
    # DB 연결을 사용하기 전에 핑 확인
    # 연결이 끊겨있으면 재연결로 "Server closed the connection unexpectedly" 에러 방지
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 3. 세션 팩토리 (DB 작업 창구)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """
    테이블 생성
    """
    print("🔄 데이터베이스 테이블 초기화 및 점검 중...")

    # Circular Import 에러 방지
    from server.core.models import Base

    Base.metadata.create_all(bind=engine)
    print("✅ 테이블 준비 완료!")


# 4. FastAPI Dependency (요청별 세션 관리)
def get_db():
    """
    API 요청이 들어오면 세션을 열고(yield),
    처리가 끝나면 반드시 닫기(close).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
