"""
Database engine + session setup.

Using SQLite for local dev (zero setup). Switching to Postgres later is a
one-line change to DATABASE_URL -- the rest of the app doesn't change.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./emergency.db")

# check_same_thread=False is needed only for SQLite (FastAPI uses multiple threads)
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a DB session and guarantees it's closed
    after the request, even if an exception is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
