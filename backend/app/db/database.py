import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


# Load the environment variables
project_root = Path(__file__).resolve().parents[3]
load_dotenv(project_root / ".env")

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL is missing")

# Connect SQLAlchemy to Supabase PostgreSQL
engine = create_engine(
    database_url,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True
)

# Create database sessions
SessionLocal = sessionmaker(bind=engine)


# Provide a database session
def get_db():
    with SessionLocal() as db:
        yield db


# Test the database connection
def check_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()