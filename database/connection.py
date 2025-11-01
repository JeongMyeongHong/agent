import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from contextlib import contextmanager
from typing import Generator

from .models import Base

# 환경 변수 로드
load_dotenv()


class DatabaseConfig:
    """데이터베이스 설정"""

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "stock_analysis")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "postgres")

    @property
    def database_url(self) -> str:
        """PostgreSQL 연결 URL 생성"""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


# 전역 설정
config = DatabaseConfig()

# SQLAlchemy 엔진 생성
engine = create_engine(
    config.database_url,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 연결 상태 체크
    echo=False,  # SQL 로깅 (개발 시 True로 변경 가능)
)

# 세션 팩토리
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """데이터베이스 테이블 초기화"""
    try:
        Base.metadata.create_all(bind=engine)
        print("[DB] 데이터베이스 테이블 초기화 완료")
    except Exception as e:
        print(f"[DB] 테이블 초기화 실패: {e}")
        raise


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 컨텍스트 매니저

    사용 예시:
        with get_db() as db:
            db.query(StockAnalysisCache).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[DB] 트랜잭션 롤백: {e}")
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    FastAPI Dependency용 세션 생성기

    사용 예시:
        @app.get("/")
        def endpoint(db: Session = Depends(get_db_session)):
            ...
    """
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # FastAPI가 자동으로 close 처리
