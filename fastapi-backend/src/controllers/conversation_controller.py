from typing import List, cast
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from sqlalchemy.orm import aliased

from src.controllers.base_controller import BaseController
from src.models.chat_model import Conversation
from src.models.user_model import User


class ConversationController(BaseController):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Conversation)

    async def list_for_user(
        self, user_id: int, *, limit: int = 50, offset: int = 0
    ) -> List[Conversation]:
        stmt = (
            select(Conversation)
            .where(
                or_(Conversation.user1_id == user_id, Conversation.user2_id == user_id)
            )
            .order_by(Conversation.id.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def list_for_user_with_peer(
        self, user_id: int, *, limit: int = 50, offset: int = 0
    ) -> List[tuple[Conversation, User]]:
        user = aliased(User)

        on_clause = or_(
            and_(Conversation.user1_id == user_id, user.id == Conversation.user2_id),
            and_(Conversation.user2_id == user_id, user.id == Conversation.user1_id),
        )

        stmt = (
            select(Conversation, user)
            .join(user, on_clause)
            .where(
                or_(
                    Conversation.user1_id == user_id,
                    Conversation.user2_id == user_id,
                )
            )
            .order_by(Conversation.id.desc())
            .limit(limit)
            .offset(offset)
        )

        res = await self.db.execute(stmt)
        rows = cast(List[tuple[Conversation, User]], res.tuples().all())
        return rows
