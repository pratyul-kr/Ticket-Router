from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Engine connects FastAPI to PostgreSQL
engine = create_engine(DATABASE_URL)

# Each request gets its own session, then it closes
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All models inherit from this
Base = declarative_base()


def get_db():
    """Dependency that provides a DB session to each route."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()