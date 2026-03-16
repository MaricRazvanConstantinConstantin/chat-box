from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from api.services.auth import AuthService, get_auth_service
from jose.exceptions import ExpiredSignatureError
from jose import JWTError

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import UserRecord
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db), auth_service: AuthService = Depends(get_auth_service)) -> UserRecord:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")

    token = credentials.credentials
    try:
        payload = auth_service.decode_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    stmt = select(UserRecord).where(UserRecord.id == int(user_id))
    user_rec = db.execute(stmt).scalar_one_or_none()
    if not user_rec:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user_rec
