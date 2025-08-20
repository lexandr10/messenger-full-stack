from pydantic import BaseModel, Field
from typing import List, Annotated

IdsList = Annotated[List[int], Field(min_length=1, description="At least one id")]


class MessageEditIn(BaseModel):
    content: str = Field(..., min_length=1)


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str | None
    is_edited: bool
    deleted: bool


class BulkDeleteIn(BaseModel):
    ids: IdsList


class AttachmentOut(BaseModel):
    id: int
    file_name: str
    mime_type: str | None
    size_bytes: int | None
    storage: str
    file_path: str


class MessageWithAttachmentsOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: str | None
    is_edited: bool
    deleted: bool
    created_at: str
    attachments: List[AttachmentOut] = Field(default_factory=list)
