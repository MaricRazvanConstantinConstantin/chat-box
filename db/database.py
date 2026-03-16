from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings


def create_sqlite_engine(path: str | None = None):
    """Create a SQLite engine. If `path` is None, use the value from settings.

    The engine is created with `check_same_thread=False` which is
    required when using SQLite with a multithreaded web app (e.g. FastAPI).
    """
    if path is None:
        path = settings.SQLITE_DATABASE_PATH

    if not path:
        raise ValueError("SQLite database path is not set")

    connect_args = {"check_same_thread": False}
    return create_engine(f"sqlite:///{path}", connect_args=connect_args)

# def create_postgres_engine(connection_string: str | None = None):
#     if connection_string is None:
#         connection_string = settings.pg_database_url

#     if not connection_string:
#         raise ValueError("PG_DATABASE_URL environment variable is not set.")

#     return create_engine(connection_string)

Base = declarative_base()

engine = create_sqlite_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    if SessionLocal is None:
        raise ValueError("Database not configured.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
