
from sqlalchemy import inspect

from app.db.database import engine


# Display tables created inside the SQLite database
def main():
    inspector = inspect(engine)

    tables = inspector.get_table_names()

    print("Database Tables:")

    for table in tables:
        print(table)


if __name__ == "__main__":
    main()
