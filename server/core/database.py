import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

user = os.getenv("POSTGRES_USER", "user")
password = os.getenv("POSTGRES_PASSWORD", "password")
db = os.getenv("POSTGRES_DB", "ticker_db")
port = os.getenv("POSTGRES_PORT", "5432")
host = "localhost"

DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(DATABASE_URL, echo=True)

print(f"🔌 DB 엔진 생성 완료: {host}:{port}/{db}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# API가 호출될 때마다 DB 세션을 열고, 응답을 보내면 자동으로 닫기
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
