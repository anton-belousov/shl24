"""
Chat methods
"""

from logging import getLogger
from uuid import UUID, uuid4

from sqlalchemy import Result, Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession

from rag.db.sql.models import Chat, Message

logger = getLogger(__name__)


async def create_chat(db: AsyncSession) -> Chat:
    """
    Create a new chat
    """
    logger.debug("create")

    chat: Chat = Chat(id=uuid4())
    db.add(chat)
    await db.commit()
    await db.refresh(chat)

    return chat


async def get_chats(db: AsyncSession) -> Sequence[Chat]:
    """
    Get all chats
    """
    logger.debug("get_chats")

    result: Result = await db.execute(select(Chat).order_by(Chat.created_at.desc()))

    return result.scalars().all()


async def get_chat(db: AsyncSession, chat_id: UUID) -> Chat:
    """
    Get chat by id
    """
    logger.debug("get_chat, chat_id=%s", chat_id)

    result: Result = await db.execute(select(Chat).filter(Chat.id == chat_id))

    return result.scalar()


async def get_messages(db: AsyncSession, chat_id: UUID) -> Sequence[Message]:
    """
    Get chat messages
    """
    logger.debug("get_messages, chat_id=%s", chat_id)

    result: Result = await db.execute(
        select(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
    )

    return result.scalars().all()


async def create_message(
    db: AsyncSession, chat_id: UUID, message: str, is_system: bool
) -> Message:
    """
    Create a new message
    """
    logger.debug("create_message, chat_id=%s, message=%s", chat_id, message)

    message: Message = Message(
        id=uuid4(), chat_id=chat_id, message=message, is_system=is_system
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message
