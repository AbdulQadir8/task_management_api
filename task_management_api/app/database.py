from sqlmodel import create_engine, SQLModel, Session
from app.config import settings
import os

# Use PostgreSQL if available, otherwise fallback to SQLite
if settings.use_sqlite_fallback:
    DATABASE_URL = settings.fallback_database_url
else:
    DATABASE_URL = settings.database_url

engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session