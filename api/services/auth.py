from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from config import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class AuthService:
    def __init__(self, secret: str = settings.JWT_SECRET, algorithm: str = settings.JWT_ALGORITHM, expire_minutes: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES):
        self.secret = secret
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def create_access_token(self, data: Any, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = {}

        if hasattr(data, "model_dump"):
            to_encode.update(data.model_dump())
        elif isinstance(data, dict):
            to_encode.update(data)
        else:
            to_encode.update(getattr(data, "__dict__", {}))

        for k, v in list(to_encode.items()):
            if isinstance(v, datetime):
                to_encode[k] = v.isoformat()

        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=self.expire_minutes))
        to_encode.update({"exp": int(expire.timestamp())})

        encoded_jwt = jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
        return encoded_jwt

    def decode_token(self, token: str) -> dict:

        payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
        return payload


def get_auth_service() -> AuthService:
    return AuthService()
