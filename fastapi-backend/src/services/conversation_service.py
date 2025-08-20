from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from typing import List, Tuple, cast

from src.controllers.conversation_controller import ConversationController
from src.models.chat_model import Conversation
from src.models.user_model import User


class ConversationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.conversation_controller = ConversationController(db)

    async def get_or_create(
        self, current_user_id: int, partner_id: int
    ) -> Conversation:
        if current_user_id == partner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create conversation with yourself",
            )

        res_user = await self.db.execute(select(User).where(User.id == partner_id))
        if res_user.scalars().first() is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Partner not found"
            )

        u1, u2 = sorted([current_user_id, partner_id])

        q = select(Conversation).where(
            Conversation.user1_id == u1, Conversation.user2_id == u2
        )
        res = await self.db.execute(q)
        conv = res.scalars().first()
        if conv:
            return conv

        conv = Conversation(user1_id=u1, user2_id=u2)
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def list_for_user_with_peer(
        self, user_id: int, *, limit: int = 50, offset: int = 0
    ) -> List[tuple[Conversation, User]]:
        rows = await self.conversation_controller.list_for_user_with_peer(
            user_id, limit=limit, offset=offset
        )
        return cast(List[tuple[Conversation, User]], rows)

    async def list_for_user(
        self, user_id: int, *, limit: int = 50, offset: int = 0
    ) -> List[Conversation]:
        return await self.conversation_controller.list_for_user(
            user_id, limit=limit, offset=offset
        )
