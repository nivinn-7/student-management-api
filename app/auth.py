import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from .schemas import TokenData

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set")

ALGORITHM = "HS256"
ACCESS_TOKEN_TYPE = "access"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
ISSUER = os.getenv("ISSUER", "techy-app")

pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload = {
        "sub": subject, 
        "exp": expire, 
        "iat": now, 
        "type": ACCESS_TOKEN_TYPE,
        "iss": ISSUER
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY, 
            algorithms = [ALGORITHM], 
            options = {"require": ["exp", "sub", "type", "iss"]}, 
            issuer = ISSUER
        )

        if payload.get("type") != ACCESS_TOKEN_TYPE:
            return None
        
        sub: Optional[str] = payload.get("sub")
        exp: Optional[int] = payload.get("exp")
        return TokenData(sub=sub, exp=exp)
    except JWTError:
        return None