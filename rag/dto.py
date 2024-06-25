"""
Data transfer objects for chat and message
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ChatResponse(BaseModel):
    """
    Chat response
    """

    id: UUID
    created_at: datetime


class CreateMessagePayload(BaseModel):
    """
    Create message payload
    """

    message: str


class MessageResponse(BaseModel):
    """
    Message response
    """

    id: UUID
    chat_id: UUID
    message: str
    created_at: datetime
    is_system: bool
