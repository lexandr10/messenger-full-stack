from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.controllers.base_controller import BaseController
from src.models.chat_model import Message


class MessageController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def get_by_ids(self, ids: List[int]) -> List[Message]:
        if not ids:
            return []
        res = await self.db.execute(select(Message).where(Message.id.in_(ids)))
        return list(res.scalars().all())

    async def list_for_conversation(
        self,
        conversation_id: int,
        *,
        limit: int = 50,
        before_id: Optional[int] = None,
        after_id: Optional[int] = None,
        include_deleted: bool = False,
    ) -> List[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .options(selectinload(Message.attachments))
        )
        if not include_deleted:
            stmt = stmt.where(Message.deleted_at.is_(None))

        if after_id:
            stmt = (
                stmt.where(Message.id > after_id)
                .order_by(Message.id.asc())
                .limit(limit)
            )
            res = await self.db.execute(stmt)
            return list(res.scalars().all())

        if before_id:
            stmt = (
                stmt.where(Message.id < before_id)
                .order_by(Message.id.desc())
                .limit(limit)
            )
            res = await self.db.execute(stmt)
            rows = list(res.scalars().all())
            rows.reverse()
            return rows

        stmt = stmt.order_by(Message.id.desc()).limit(limit)
        res = await self.db.execute(stmt)
        rows = list(res.scalars().all())
        rows.reverse()
        return rows
