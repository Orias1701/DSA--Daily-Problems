import asyncio
import logging
import os
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database import init_db, async_session_maker
from database.repositories import (
    UserRepository,
    TicketRepository,
    VIPRepository,
)
from handlers import get_main_router
from middlewares import DbSessionMiddleware, BanMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def daily_reset():
    """Reset daily wager, cashback, withdraw count at 00:00 UTC."""
    async with async_session_maker() as session:
        from database.models import User
        from sqlalchemy import update
        await session.execute(
            update(User).values(
                daily_wager=0,
                cashback_today=0,
                withdraw_count_today=0,
                last_cashback_reset=datetime.utcnow(),
                last_withdraw_reset=datetime.utcnow(),
            )
        )
        await session.commit()
    logger.info("Daily reset done.")


async def close_stale_tickets():
    """Close tickets after 10 minutes inactivity."""
    async with async_session_maker() as session:
        ticket_repo = TicketRepository(session)
        stale = await ticket_repo.get_stale_tickets(settings.TICKET_INACTIVITY_MINUTES)
        for t in stale:
            await ticket_repo.close_ticket(t.id)
        await session.commit()
        if stale:
            logger.info("Closed %s stale tickets.", len(stale))


async def on_startup(bot: Bot) -> None:
    os.makedirs("data", exist_ok=True)
    await init_db()
    async with async_session_maker() as session:
        vip_repo = VIPRepository(session)
        await vip_repo.ensure_default_levels()
        await session.commit()
    logger.info("Bot started.")


async def on_shutdown(bot: Bot) -> None:
    logger.info("Bot stopped.")


def main() -> None:
    if not settings.BOT_TOKEN:
        raise ValueError("BOT_TOKEN is required. Copy .env.example to .env and set BOT_TOKEN.")

    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    dp.message.middleware(DbSessionMiddleware())
    dp.callback_query.middleware(DbSessionMiddleware())
    dp.message.middleware(BanMiddleware())
    dp.callback_query.middleware(BanMiddleware())

    dp.include_router(get_main_router())

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        daily_reset,
        CronTrigger(hour=settings.DAILY_RESET_HOUR, minute=0),
        id="daily_reset",
    )
    scheduler.add_job(
        close_stale_tickets,
        CronTrigger(minute="*/5"),
        id="close_tickets",
    )
    scheduler.start()

    try:
        asyncio.run(dp.start_polling(bot))
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    main()
