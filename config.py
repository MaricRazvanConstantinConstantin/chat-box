import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        )
        self.SQLITE_DATABASE_PATH: str = os.getenv(
            "SQLITE_DATABASE_PATH", "./chatbox.db"
        )
        self.FILES_DIRECTORY: str = os.getenv("FILES_DIRECTORY", "./files")


settings = Settings()
