from app.config.redis_client import get_redis
from app.models.index import Campus, User
from app.models.stores import Shop
from app.schema.users import CreateUserModel, LoginPayload, RefreshPayload
from fastapi.exceptions import HTTPException
from tortoise.exceptions import IntegrityError
from fastapi import status
from app.security.authentication import create_token, hash_password, verify_password, decode_token


ACCESS_TYPE = "access"
REFRESH_TYPE = "refresh"

async def get_users():
    return await User.all()

async def create_user(payload: CreateUserModel):
    campus = await Campus.get_or_none(name=payload.campus_name)
    
    try:
        account = await User.create(
            email=payload.email,
            name=payload.name,
            password=hash_password(payload.password),
            campus=campus
   

        )
    except IntegrityError:
        raise HTTPException(detail=f"Email {payload.email} already taken", status_code=400)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    return account

async def login_user(payload: LoginPayload):
    user = await User.get_or_none(email=payload.email)
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    sub = str(user.email)
    access_token = create_token(sub=sub, token_type=ACCESS_TYPE)
    refresh_token = create_token(sub=sub, token_type=REFRESH_TYPE)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    
async def blacklist_token(jti: str, expires_in_seconds: int):
    r = await get_redis()
    await r.set(f"bl:{jti}", "1", ex=expires_in_seconds)

async def is_token_blacklisted(jti: str) -> bool:
    r = await get_redis()
    res = await r.get(f"bl:{jti}")
    return res is not None

async def refresh_tokens(payload: RefreshPayload):
    from jose import JWTError
    try:
        payload = decode_token(payload.refresh_token)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if payload.get("type") != REFRESH_TYPE:
        raise HTTPException(status_code=401, detail="Not a refresh token")

    jti = payload.get("jti")
    if await is_token_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    sub = payload.get("sub")
    user = await User.get_or_none(email=sub)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    exp = int(payload.get("exp"))
    now_ts = __import__("time").time()
    ttl = int(exp - now_ts) if exp > now_ts else 0
    if ttl > 0:
        await blacklist_token(jti, ttl)
    new_access = create_token(sub=sub, token_type=ACCESS_TYPE, extra={"role": user.role})
    new_refresh = create_token(sub=sub, token_type=REFRESH_TYPE)
    return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}

async def logout(token: str):
    from jose import JWTError
    try:
        payload = decode_token(token)
    except JWTError:
        return

    jti = payload.get("jti")
    exp = int(payload.get("exp"))
    now_ts = __import__("time").time()
    ttl = int(exp - now_ts) if exp > now_ts else 0
    if ttl > 0:
        await blacklist_token(jti, ttl)

async def logout_all_for_user(user_email: str):
    r = await get_redis()
    await r.set(f"user:revoked:{user_email}", str(__import__("time").time()))

