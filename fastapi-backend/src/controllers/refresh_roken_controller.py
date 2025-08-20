import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.controllers.base_controller import BaseController
from src.models.user_model import RefreshToken

logger = logging.getLogger("uvicorn.error")


class RefreshTokenController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RefreshToken)

    async def get_token_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(self.model).where(RefreshToken.token_hash == token_hash)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_token(
        self, token_hash: str, current_time: datetime
    ) -> RefreshToken | None:
        stmt = select(self.model).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.expires_at > current_time,
            RefreshToken.revoked_at == None,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_token(
        self, user_id: int, token_hash: str, expires_at: datetime
    ) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id, token_hash=token_hash, expires_at=expires_at
        )
        self.db.add(refresh_token)
        return await self.create(refresh_token)

    async def revoke_token(self, refresh_token: RefreshToken) -> None:
        refresh_token.revoked_at = datetime.now(timezone.utc)
        await self.db.commit()
