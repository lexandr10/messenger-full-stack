import jwt
from fastapi import HTTPException, status, Request, Response, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt
from datetime import datetime

from src.conf.config import settings
from src.controllers.user_controller import UserController
from src.controllers.refresh_roken_controller import RefreshTokenController
from src.schemas.user_schema import UserSchema, AuthResponse
from src.models.user_model import User
from src.services.refresh_token_service import RefreshTokenService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_controller = UserController(self.db)
        self.refresh_token_service = RefreshTokenService(self.db)

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    async def register_user(self, user: UserSchema) -> tuple[str, str, datetime]:
        exist_username = await self.user_controller.get_user_by_username(user.username)
        if exist_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="User already exists"
            )

        exist_email = await self.user_controller.get_user_by_email(user.email)
        if exist_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )

        hashed_password = self._hash_password(user.password)
        created_user = await self.user_controller.create_user(user, hashed_password)

        access_token = await self.refresh_token_service.create_access_token(
            created_user.username
        )

        refresh_raw, refresh_expires = (
            await self.refresh_token_service.create_refresh_token(created_user.id)
        )

        return access_token, refresh_raw, refresh_expires

    async def login_user(self, email: str, password: str) -> tuple[str, str, datetime]:
        user = await self.user_controller.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        if not self._verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        access_token = await self.refresh_token_service.create_access_token(
            user.username
        )
        refresh_raw, refresh_expires = (
            await self.refresh_token_service.create_refresh_token(user.id)
        )

        return access_token, refresh_raw, refresh_expires

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
        user = await self.user_controller.get_user_by_username(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user

    async def refresh(self, req: Request):
        access_token, refresh_raw, refresh_expires = (
            await self.refresh_token_service.refresh(req)
        )

        return access_token, refresh_raw, refresh_expires

    async def logout(self, req: Request, response: Response):
        refresh_token = req.cookies.get("refresh_token")
        if refresh_token:
            try:
                await self.refresh_token_service.revoke_refresh_token(refresh_token)
                response.delete_cookie(key="refresh_token", path="/")
            except HTTPException:
                pass
            except Exception:
                pass

        return True
