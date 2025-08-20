from pydantic import BaseModel, EmailStr, Field, constr
from datetime import datetime


class UserSchema(BaseModel):
    username: str = Field(min_length=6, max_length=20, description="Username")
    email: EmailStr
    password: constr(min_length=6, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CurrentUser(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime
