
from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker


# Set the location for our SQLite database
backend_folder = Path(__file__).resolve().parents[2]
database_path = backend_folder / "scoperipple.db"

database_url = f"sqlite:///{database_path}"

# Create the SQLite database engine
engine = create_engine(database_url)


# Enable foreign key validation
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Create sessions for database operations
SessionLocal = sessionmaker(bind=engine)


# Provide a database session
def get_db():
    with SessionLocal() as db:
        yield db


# Verify the database connection
def check_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return result.scalar()
