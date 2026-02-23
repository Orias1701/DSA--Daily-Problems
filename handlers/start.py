from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

from config import settings
from database.repositories import UserRepository, VIPRepository
from keyboards import main_menu_keyboard
from utils import format_currency
from utils.texts import welcome_new_user, welcome_returning_user

router = Router(name="start")


async def _get_vip_name_async(level: int, vip_repo: VIPRepository) -> str:
    vip = await vip_repo.get_by_level(level)
    return vip.name if vip else "Đồng"


@router.message(CommandStart())
async def cmd_start(message: Message, session) -> None:
    user_repo = UserRepository(session)
    vip_repo = VIPRepository(session)
    user = await user_repo.get_or_create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name or "User",
    )
    name = user.first_name or "User"
    is_new = not user.welcome_bonus_given
    if is_new:
        user.welcome_bonus_given = True
        await user_repo.add_balance(user.id, settings.WELCOME_BONUS)
        await session.flush()
    await session.commit()
    if is_new:
        text = welcome_new_user(name)
    else:
        vip_name = await _get_vip_name_async(user.vip_level, vip_repo)
        cashback_pct = f"{settings.CASHBACK_RATE * 100:.1f}".rstrip("0").rstrip(".")
        text = welcome_returning_user(
            name=name,
            balance=format_currency(user.balance),
            vip_name=vip_name,
            cashback_rate=cashback_pct,
            withdraw_count_today=user.withdraw_count_today,
            max_withdraw_per_day=settings.MAX_WITHDRAW_PER_DAY,
        )

    await message.answer(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery, session) -> None:
    user_repo = UserRepository(session)
    vip_repo = VIPRepository(session)
    user = await user_repo.get_by_id(callback.from_user.id)
    if not user:
        await callback.answer("Lỗi. Gửi /start")
        return
    name = user.first_name or "User"
    vip_name = await _get_vip_name_async(user.vip_level, vip_repo)
    cashback_pct = f"{settings.CASHBACK_RATE * 100:.1f}".rstrip("0").rstrip(".")
    text = welcome_returning_user(
        name=name,
        balance=format_currency(user.balance),
        vip_name=vip_name,
        cashback_rate=cashback_pct,
        withdraw_count_today=user.withdraw_count_today,
        max_withdraw_per_day=settings.MAX_WITHDRAW_PER_DAY,
    )
    await callback.message.edit_text(
        text,
        reply_markup=main_menu_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
