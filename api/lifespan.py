from fastapi.concurrency import asynccontextmanager
from fastapi import FastAPI
from db.database import Base, engine
from sqlalchemy import text

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan function to initialize the database at app startup."""
    print('\n' + '=' * 50)
    print("Starting up the app and initializing the database...")
    print('=' * 50 + '\n')

    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            print("Database connection verified successfully.")
    except Exception as e:
        print(f"Error verifying database connection: {e}")
        raise

    yield

    engine.dispose()
    print('\n' + '=' * 50)
    print("Shutting down the app and disposing of the database engine...")
    print('=' * 50 + '\n')
