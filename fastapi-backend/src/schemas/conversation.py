from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ConversationCreate(BaseModel):
    partner_id: int = Field(..., ge=1)


class ConversationOut(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLiteOut(BaseModel):
    id: int
    username: Optional[str] = None
    email: Optional[str] = None


class ConversationWithPeerOut(ConversationOut):
    peer: Optional[UserLiteOut] = None
