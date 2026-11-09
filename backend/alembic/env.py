
from alembic import context
from sqlalchemy import pool
from sqlalchemy import create_engine, event

from app.db.database import database_url
from app.db.models import Base


# Load Alembic configuration
config = context.config

# Use our SQLAlchemy database models
target_metadata = Base.metadata


# Enable foreign key checks for SQLite connections
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Run migrations without a database connection
def run_migrations_offline():
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


# Run migrations using a database connection
def run_migrations_online():
    engine = create_engine(
        database_url,
        poolclass=pool.NullPool
    )

    event.listen(engine, "connect", enable_foreign_keys)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True
        )

        with context.begin_transaction():
            context.run_migrations()

    engine.dispose()


# Choose the appropriate migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
