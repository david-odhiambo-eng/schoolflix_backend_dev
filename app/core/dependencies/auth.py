from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

from app.config.redis_client import get_redis
from app.models.index import User
from app.security.authentication import decode_token
from app.services.users import is_token_blacklisted


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exception

    jti = payload.get("jti")
    if await is_token_blacklisted(jti):
        raise credentials_exception

    sub = payload.get("sub")
    if not sub:
        raise credentials_exception

    user = await User.get_or_none(email=sub)
    if not user:
        raise credentials_exception
    r = await get_redis()
    revoked = await r.get(f"user:revoked:{user.email}")
    if revoked:
        iat = payload.get("iat")
        if iat is not None:
            try:
                iat_ts = float(iat)
            except Exception:
                iat_ts = None
            if iat_ts and float(revoked) > iat_ts:
                raise credentials_exception

    return user

def require_roles(*allowed_roles: str):
    async def role_dependency(current_user: User = Depends(get_current_user)):
        if getattr(current_user, "role", None) not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient privileges")
        return current_user
    return role_dependency
