import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm


from src.core.depend_service import get_auth_service, get_current_user
from src.schemas.user_schema import AuthResponse, UserSchema, CurrentUser
from src.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger("uvicorn.error")


@router.get("/me", response_model=CurrentUser)
async def me(current_user=Depends(get_current_user)):
    return current_user


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserSchema,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token, refresh_raw, refresh_expires = await auth_service.register_user(data)

    max_age = int((refresh_expires - datetime.now(timezone.utc)).total_seconds())
    response.set_cookie(
        key="refresh_token",
        value=refresh_raw,
        max_age=max_age,
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login", response_model=AuthResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    response: Response = None,
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token, refresh_raw, refresh_expires = await auth_service.login_user(
        form_data.username, form_data.password
    )
    max_age = int((refresh_expires - datetime.now(timezone.utc)).total_seconds())
    response.set_cookie(
        key="refresh_token",
        value=refresh_raw,
        max_age=max_age,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    req: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    access_token, refresh_raw, refresh_expires = await auth_service.refresh(req)
    max_age = int((refresh_expires - datetime.now(timezone.utc)).total_seconds())
    response.set_cookie(
        key="refresh_token",
        value=refresh_raw,
        max_age=max_age,
        httponly=True,
        secure=False,
        samesite="lax",
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.logout(request, response)
