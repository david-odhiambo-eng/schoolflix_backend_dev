from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies.auth import get_current_user
from app.schema.users import CreateUserModel, LoginPayload, RefreshPayload, TokenOut
from app.services.users import create_user, get_users, login_user, logout, logout_all_for_user, refresh_tokens

router = APIRouter()

@router.get("/")
async def users():
    return await get_users()

@router.post("/register")
async def create(payload: CreateUserModel):
    account = await create_user(payload)
    return {"id": str(account.id), "email": account.email}

@router.post("/login", response_model=TokenOut)
async def login(payload: LoginPayload):
    return await login_user(payload)

@router.post("/refresh", response_model=TokenOut)
async def refresh(payload: RefreshPayload):
    return await refresh_tokens(payload)

@router.post("/logout")
async def logout_route(token: str):
    raise HTTPException(status_code=501, detail="Prefer calling /auth/logout with Authorization: Bearer <token>")

@router.post("/logout_token")
async def logout_token(payload: RefreshPayload):
    await logout(payload.refresh_token)
    return {"message": "Token revoked"}

@router.post("/logout_all")
async def logout_all_route(current_user = Depends(get_current_user)):
    await logout_all_for_user(current_user.email)
    return {"message": "All sessions revoked"}

@router.get("/me")
async def me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role
    }
