from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)
        user = getattr(event, "from_user", None)
        if not user:
            return await handler(event, data)
        result = await session.execute(select(User).where(User.id == user.id))
        db_user = result.scalar_one_or_none()
        if db_user and db_user.is_banned:
            if isinstance(event, Message):
                await event.answer(
                    "🚫 Bạn đã bị khóa tài khoản. Liên hệ hỗ trợ nếu cần."
                )
            return
        return await handler(event, data)
