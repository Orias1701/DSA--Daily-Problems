from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import settings
from database.repositories import UserRepository, BetRepository, VIPRepository
from keyboards import profile_keyboard, main_menu_keyboard
from utils import format_currency
from utils.texts import profile_text, help_text

router = Router(name="profile")

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


def _win_rate(wins: int, losses: int) -> str:
    total = wins + losses
    if total == 0:
        return "0"
    return f"{(wins / total) * 100:.1f}"


@router.callback_query(F.data == "profile")
async def cb_profile(callback: CallbackQuery, session) -> None:
    user_repo = UserRepository(session)
    vip_repo = VIPRepository(session)
    user = await user_repo.get_by_id(callback.from_user.id)
    if not user:
        await callback.answer("Gửi /start trước.")
        return
    vip = await vip_repo.get_by_level(user.vip_level)
    vip_name = vip.name if vip else "Đồng"
    text = profile_text(
        balance=format_currency(user.balance),
        total_deposit=format_currency(user.total_deposit),
        total_withdraw=format_currency(user.total_withdraw),
        total_wager=format_currency(user.total_wager),
        profit=format_currency(user.total_profit),
        wins=user.wins,
        losses=user.losses,
        win_rate=_win_rate(user.wins, user.losses),
        cashback_today=format_currency(user.cashback_today),
        vip_name=vip_name,
        withdraw_today=user.withdraw_count_today,
        max_withdraw=settings.MAX_WITHDRAW_PER_DAY,
    )
    await callback.message.edit_text(
        text,
        reply_markup=profile_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "show_bets")
async def cb_show_bets(callback: CallbackQuery, session) -> None:
    bet_repo = BetRepository(session)
    bets = await bet_repo.get_by_user(callback.from_user.id, limit=20)
    if not bets:
        await callback.answer("Chưa có lịch sử cược.", show_alert=True)
        return
    lines = []
    for b in bets[:15]:
        res = "✅" if b.won else "❌"
        lines.append(
            f"{res} {b.choice.upper()} {format_currency(b.amount)} → "
            f"{b.dice1}+{b.dice2}+{b.dice3}={b.total} ({format_currency(b.profit)})"
        )
    text = "📊 <b>LỊCH SỬ CƯỢC</b>\n\n" + "\n".join(lines)
    await callback.message.edit_text(
        text,
        reply_markup=profile_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(help_text(), parse_mode="HTML", reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "help")
async def cb_help(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        help_text(),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()
