import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.controllers.base_controller import BaseController
from src.models.user_model import User
from src.schemas.user_schema import UserSchema

logger = logging.getLogger("uvicorn.error")


class UserController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(self.model).filter_by(username=username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email) -> User | None:
        stmt = select(self.model).filter_by(email=email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(self, user: UserSchema, hash_password: str) -> User:
        new_user = User(
            **user.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=hash_password
        )
        return await self.create(new_user)

    async def get_user_by_id(self, _id: int) -> User | None:
        stmt = select(self.model).filter_by(id=_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
