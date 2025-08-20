from datetime import timedelta, datetime, timezone


from fastapi import HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
import jwt
import secrets

from src.controllers.refresh_roken_controller import RefreshTokenController
from src.conf.config import settings
from src.controllers.user_controller import UserController
from src.models.user_model import User


class RefreshTokenService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.refresh_token_controller = RefreshTokenController(self.db)
        self.user_controller = UserController(self.db)

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    async def create_access_token(self, username: str) -> str:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode = {"exp": expire, "sub": username}
        encode_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encode_jwt

    async def create_refresh_token(self, user_id: int) -> tuple[str, datetime]:
        raw_token = secrets.token_urlsafe(48)
        token_hash = self._hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self.refresh_token_controller.create_token(
            user_id, token_hash, expires_at
        )
        return raw_token, expires_at

    def decode_and_verify_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    async def refresh(self, req: Request):
        token = req.cookies.get("refresh_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user = await self.validate_refresh_token(token)

        token_hash = self._hash_token(token)
        current_time = datetime.now(timezone.utc)
        refresh_obj = await self.refresh_token_controller.get_active_token(
            token_hash, current_time
        )
        if refresh_obj:
            await self.refresh_token_controller.revoke_token(refresh_obj)

        access_token = await self.create_access_token(user.username)
        refresh_raw, refresh_expires = await self.create_refresh_token(user.id)

        return access_token, refresh_raw, refresh_expires

    async def validate_refresh_token(self, token: str) -> User:
        token_hash = self._hash_token(token)
        current_time = datetime.now(timezone.utc)
        refresh_token = await self.refresh_token_controller.get_active_token(
            token_hash, current_time
        )
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )
        if not refresh_token.user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user = await self.user_controller.get_user_by_id(refresh_token.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def revoke_refresh_token(self, token: str) -> None:
        token_hash = self._hash_token(token)
        refresh_token = await self.refresh_token_controller.get_token_by_hash(
            token_hash
        )
        if refresh_token and not refresh_token.revoked_at:
            await self.refresh_token_controller.revoke_token(refresh_token)
        return None
