import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def _database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set")
    return url

engine = create_engine(_database_url(), future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)