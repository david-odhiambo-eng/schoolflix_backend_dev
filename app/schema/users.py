from pydantic import BaseModel, EmailStr

class CreateUserModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    campus_name: str|None = None
    

class LoginPayload(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshPayload(BaseModel):
    refresh_token: str