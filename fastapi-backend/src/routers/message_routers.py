from fastapi import APIRouter, Depends
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.depend_service import get_current_user
from src.database.db import get_db
from src.models.chat_model import Message
from src.schemas.message import MessageEditIn, MessageOut, BulkDeleteIn
from src.services.message_service import MessageService
from src.sockets.hub import manager

router = APIRouter(prefix="/messages", tags=["message"])


def _to_out(msg) -> MessageOut:
    return MessageOut(
        id=msg.id,
        conversation_id=msg.conversation_id,
        sender_id=msg.sender_id,
        content=msg.content,
        is_edited=msg.is_edited,
        deleted=msg.deleted_at is not None,
    )


@router.patch("/{message_id}", response_model=MessageOut)
async def edit_message(
    message_id: int,
    payload: MessageEditIn,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = MessageService(db)
    msg = await svc.edit_message(
        current_user_id=current_user.id, message_id=message_id, content=payload.content
    )
    await manager.broadcast(
        msg.conversation_id,
        {
            "type": "message:edited",
            "message": {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "sender_id": msg.sender_id,
                "content": msg.content,
                "is_edited": True,
                "deleted": msg.deleted_at is not None,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            },
        },
    )

    return _to_out(msg)


@router.delete("/bulk")
async def delete_message_bulk(
    payload: BulkDeleteIn,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> Dict[str, List[int]]:
    svc = MessageService(db)
    result = await svc.delete_message_bulk(
        current_user_id=current_user.id, ids=payload.ids
    )
    if result["deleted"]:
        rows = await db.execute(
            select(Message.id, Message.conversation_id).where(
                Message.id.in_(result["deleted"])
            )
        )
        by_conv: dict[int, list[int]] = {}
        for mid, cid in rows.all():
            by_conv.setdefault(cid, []).append(mid)

        for cid, mids in by_conv.items():
            await manager.broadcast(
                cid, {"type": "message:deleted", "message_ids": mids}
            )
    return result
