from datetime import  datetime
import datetime as dt
from uuid import uuid4
from argon2 import PasswordHasher, exceptions as argon_exception

from jose import JWTError, jwt

from app.config.settings import settings

password_hasher = PasswordHasher()

def hash_password(password: str)-> str:
    return password_hasher.hash(password)

def verify_password(password: str, hashed: str)-> bool:
    try:
        return password_hasher.verify(hashed, password)
    except argon_exception.VerifyMismatchError:
        return False
    except Exception:
        return False

def create_token(sub: str, token_type: str="access", extra: dict=None)-> str:
    now = datetime.now(tz=dt.UTC)
    expire = (now + settings.ACCESS_TOKEN_EXPIRE) if token_type == "access" else (now + settings.REFRESH_TOKEN_EXPIRE)
    payload = {
        "sub": sub,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": now,
        "exp": expire
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str)-> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise e
    return payload