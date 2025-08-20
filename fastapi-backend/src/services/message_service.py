from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from datetime import datetime, timezone
from typing import Dict, List, Any, Iterable, Optional

from src.controllers.message_controller import MessageController
from src.models.chat_model import Message, Conversation


def _normalize_ids(raw_ids: Iterable[Any]) -> List[int]:
    out: set[int] = set()
    for x in raw_ids:
        try:
            v = int(x)
            if v > 0:
                out.add(v)
        except (TypeError, ValueError):
            continue
    return sorted(out)


class MessageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.message_controller = MessageController(self.db)

    async def edit_message(
        self, *, current_user_id: int, message_id: int, content: str
    ) -> Message:
        msg = await self.message_controller.get_by_id(message_id)
        if not msg or msg.deleted_at is not None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Message not found"
            )
        if msg.sender_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not the author"
            )

        new_content = (content or "").strip()
        if not new_content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Empty content"
            )

        msg.content = new_content
        msg.is_edited = True
        msg.updated_at = datetime.now(timezone.utc)

        await self.message_controller.update(msg)

        return msg

    async def delete_message_bulk(
        self, *, current_user_id: int, ids: list[int]
    ) -> Dict[str, List[int]]:
        uniq_ids: List[int] = _normalize_ids(ids)
        if not uniq_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Empty ids"
            )

        msgs: List[Message] = await self.message_controller.get_by_ids(uniq_ids)

        found_ids = {m.id for m in msgs}
        not_found = [i for i in uniq_ids if i not in found_ids]
        forbidden = [m.id for m in msgs if m.sender_id != current_user_id]

        now = datetime.now(timezone.utc)
        to_delete: List[Message] = [
            m for m in msgs if m.sender_id == current_user_id and m.deleted_at is None
        ]

        for m in to_delete:
            m.deleted_at = now

        if to_delete:
            await self.db.commit()

        return {
            "deleted": [m.id for m in to_delete],
            "forbidden": forbidden,
            "not_found": not_found,
        }

    async def _ensure_membership(self, conversation_id: int, user_id: int) -> None:
        res = await self.db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = res.scalars().first()
        if not conv or user_id not in (conv.user1_id, conv.user2_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not in conversation"
            )

    async def list_messages(
        self,
        *,
        conversation_id: int,
        user_id: int,
        limit: int = 50,
        before_id: Optional[int] = None,
        after_id: Optional[int] = None,
    ) -> List[Message]:
        await self._ensure_membership(conversation_id, user_id)
        limit = max(1, min(limit, 100))
        return await self.message_controller.list_for_conversation(
            conversation_id,
            limit=limit,
            before_id=before_id,
            after_id=after_id,
            include_deleted=False,
        )
