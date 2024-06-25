"""
Message handler
"""

from logging import getLogger
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from rag.db.sql.models import Chat, Message
from rag.modules import agent, router
from rag.service import chat

logger = getLogger(__name__)


async def process_user_message(
    db: AsyncSession, chat_id: UUID, message: str
) -> Message:
    """
    Process user message
    """
    logger.debug("process_user_message, chat_id=%s, message=%s", chat_id, message)
    existing_chat: Chat = await chat.get_chat(db, chat_id)

    if not existing_chat:
        raise ValueError("Chat not found")

    await chat.create_message(db, chat_id, message, False)
    response: str = router.run(message)

    return await chat.create_message(db, chat_id, response, True)
