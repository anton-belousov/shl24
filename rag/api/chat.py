from logging import getLogger
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from rag.db.sql.connection import get_db
from rag.db.sql.models import Chat, Message
from rag.dto import ChatResponse, CreateMessagePayload, MessageResponse
from rag.service import chat
from rag.service.handler import process_user_message

router: APIRouter = APIRouter()
logger = getLogger(__name__)


@router.get("", response_model=list[ChatResponse])
async def get_chats(db: AsyncSession = Depends(get_db)) -> list[Chat]:
    """
    Get chats
    """
    logger.debug("get_chats")
    return await chat.get_chats(db)


@router.post("", response_model=ChatResponse)
async def create_chat(
    db: AsyncSession = Depends(get_db),
) -> Chat:
    """
    Create a new chat
    """
    logger.debug("create_chat")
    return await chat.create_chat(db)


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def create_message(
    chat_id: UUID,
    payload: CreateMessagePayload,
    db: AsyncSession = Depends(get_db),
) -> Message:
    """
    Create a new message
    """
    logger.debug("create_message, chat_id=%s, payload=%s", chat_id, payload)

    existing_chat: Chat = await chat.get_chat(db, chat_id)

    if not existing_chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return await process_user_message(db, chat_id, payload.message)


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    chat_id: UUID, db: AsyncSession = Depends(get_db)
) -> list[Message]:
    """
    Get chat messages
    """
    logger.debug("get_messages, chat_id=%s", chat_id)

    existing_chat: Chat = await chat.get_chat(db, chat_id)

    if not existing_chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return await chat.get_messages(db, chat_id)
