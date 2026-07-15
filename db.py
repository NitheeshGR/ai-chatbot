# Database engine, session factory, and base class for SQLAlchemy models
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DATABASE_URL

# Create database engine using the PostgreSQL connection string
engine = create_engine(DATABASE_URL)

# Session factory — call SessionLocal() to get a new DB session for queries
SessionLocal = sessionmaker(bind=engine)


# Base class for all models — all tables inherit from this
class Base(DeclarativeBase):
    pass
