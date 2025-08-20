from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.core.depend_service import get_current_user
from src.database.db import get_db
from src.schemas.conversation import (
    ConversationOut,
    ConversationCreate,
    ConversationWithPeerOut,
    UserLiteOut,
)
from src.schemas.message import MessageWithAttachmentsOut, AttachmentOut
from src.services.conversation_service import ConversationService
from src.services.message_service import MessageService

router = APIRouter(prefix="/conversations", tags=["conversation"])


def _to_out(m) -> MessageWithAttachmentsOut:
    return MessageWithAttachmentsOut(
        id=m.id,
        conversation_id=m.conversation_id,
        sender_id=m.sender_id,
        content=m.content,
        is_edited=m.is_edited,
        deleted=m.deleted_at is not None,
        created_at=m.created_at.isoformat() if m.created_at else "",
        attachments=[
            AttachmentOut(
                id=a.id,
                file_name=a.file_name,
                mime_type=a.mime_type,
                size_bytes=a.size_bytes,
                storage=a.storage,
                file_path=a.file_path,
            )
            for a in (m.attachments or [])
        ],
    )


@router.post("", response_model=ConversationOut)
async def get_or_create_conversation(
    payload: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = ConversationService(db)
    conv = await svc.get_or_create(current_user.id, payload.partner_id)
    return ConversationOut(id=conv.id, user1_id=conv.user1_id, user2_id=conv.user2_id)


@router.get(
    "/{conversation_id}/messages", response_model=List[MessageWithAttachmentsOut]
)
async def list_messages(
    conversation_id: int,
    limit: int = Query(50, ge=1, le=100),
    before_id: Optional[int] = Query(None),
    after_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = MessageService(db)
    items = await svc.list_messages(
        conversation_id=conversation_id,
        user_id=current_user.id,
        limit=limit,
        before_id=before_id,
        after_id=after_id,
    )
    return [_to_out(m) for m in items]


@router.get("", response_model=List[ConversationWithPeerOut])
async def list_conversations(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    svc = ConversationService(db)
    rows = await svc.list_for_user_with_peer(
        user_id=current_user.id, limit=limit, offset=offset
    )

    out: List[ConversationWithPeerOut] = []
    for conv, peer in rows:
        out.append(
            ConversationWithPeerOut(
                id=conv.id,
                user1_id=conv.user1_id,
                user2_id=conv.user2_id,
                created_at=conv.created_at,
                peer=UserLiteOut(
                    id=peer.id,
                    username=getattr(peer, "username", None),
                    email=getattr(peer, "email", None),
                ),
            )
        )
    return out
