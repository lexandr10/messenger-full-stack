from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from src.database.db import get_db
from src.sockets.hub import manager
from src.sockets.auth_ws import authenticate_ws
from src.models.chat_model import Conversation, Message, Attachment

ws_router = APIRouter()


async def _user_in_conversation(
    db: AsyncSession, conversation_id: int, user_id: int
) -> bool:
    res = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = res.scalars().first()
    return bool(conv and user_id in (conv.user1_id, conv.user2_id))


@ws_router.websocket("/ws/conversation/{conversation_id}")
async def chat_ws(
    ws: WebSocket, conversation_id: int, db: AsyncSession = Depends(get_db)
):
    user = await authenticate_ws(ws, db)
    if not user:
        return

    if not await _user_in_conversation(db, conversation_id, user.id):
        await ws.close(
            code=status.WS_1008_POLICY_VIOLATION, reason="User not in conversation"
        )
        return

    await manager.connect(conversation_id, ws)

    await ws.send_json(
        {"type": "connected", "conversation_id": conversation_id, "user_id": user.id}
    )

    try:
        while True:
            incoming = await ws.receive_json()

            if incoming.get("type") == "send_message":
                content = (incoming.get("content") or "").strip()

                raw_atts = incoming.get("attachments") or []
                if not isinstance(raw_atts, list):
                    await ws.send_json(
                        {"type": "error", "message": "Invalid attachments"}
                    )
                    continue
                normalized_atts = []
                bad = False
                for i, a in enumerate(raw_atts):
                    if not isinstance(a, dict) or not a.get("file_path"):
                        await ws.send_json(
                            {"type": "error", "message": "Invalid attachment"}
                        )
                        bad = True
                        break
                    normalized_atts.append(
                        {
                            "file_name": a.get("file_name") or "file",
                            "mime_type": a.get("mime"),
                            "size_bytes": a.get("size_bytes"),
                            "storage": a.get("storage") or "cloudinary",
                            "file_path": a["file_path"],
                        }
                    )
                if bad:
                    continue
                if not content and not normalized_atts:
                    await ws.send_json(
                        {"type": "error", "message": "Content or attachments required"}
                    )
                    continue

                reply_to_id = incoming.get("reply_to_id")
                if reply_to_id is not None and not isinstance(reply_to_id, int):
                    await ws.send_json(
                        {"type": "error", "message": "Invalid reply_to_id"}
                    )
                    continue

                msg = Message(
                    conversation_id=conversation_id,
                    sender_id=user.id,
                    content=content or None,
                    created_at=datetime.now(timezone.utc),
                    reply_to_id=reply_to_id,
                )
                db.add(msg)
                await db.commit()
                await db.refresh(msg)

                created_atts = []
                if normalized_atts:
                    for a in normalized_atts:
                        att = Attachment(
                            message_id=msg.id,
                            file_name=a["file_name"],
                            mime_type=a["mime_type"],
                            size_bytes=a["size_bytes"],
                            storage=a["storage"],
                            file_path=a["file_path"],
                        )
                        db.add(att)
                        created_atts.append(att)
                    await db.commit()
                    for att in created_atts:
                        await db.refresh(att)

                await manager.broadcast(
                    conversation_id,
                    {
                        "type": "message:new",
                        "message": {
                            "id": msg.id,
                            "conversation_id": conversation_id,
                            "sender_id": user.id,
                            "content": msg.content,
                            "attachments": [
                                {
                                    "id": att.id,
                                    "file_name": att.file_name,
                                    "mime_type": att.mime_type,
                                    "size_bytes": att.size_bytes,
                                    "storage": att.storage,
                                    "file_path": att.file_path,
                                }
                                for att in created_atts
                            ],
                            "created_at": msg.created_at.isoformat(),
                            "is_edited": False,
                            "deleted": False,
                        },
                    },
                )
            else:
                await ws.send_json({"type": "echo", "data": incoming})
    except WebSocketDisconnect:
        await manager.disconnect(conversation_id, ws)
