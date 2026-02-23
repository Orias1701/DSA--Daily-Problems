from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, func

from config import settings
from database.models import User, Transaction, Bet
from database.repositories import (
    UserRepository,
    TransactionRepository,
    BetRepository,
    VIPRepository,
    CouponRepository,
    TicketRepository,
    AdminLogRepository,
)
from keyboards import admin_main_keyboard, approve_reject_keyboard, main_menu_keyboard
from states import AdminStates
from utils import format_currency

router = Router(name="admin")

SEP = "━━━━━━━━━━━━━━━━━━━━━━"

MAINTENANCE_KEY = "maintenance_mode"


def admin_only(func):
    async def wrapper(event, *args, **kwargs):
        user_id = event.from_user.id if hasattr(event, "from_user") else None
        if not user_id or user_id not in settings.ADMIN_IDS:
            if hasattr(event, "answer"):
                await event.answer("⛔ Bạn không có quyền truy cập.")
            return
        return await func(event, *args, **kwargs)
    return wrapper


@router.message(Command("admin"))
async def cmd_admin(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        await message.answer("⛔ Bạn không có quyền truy cập.")
        return
    await message.answer(
        "👑 <b>ADMIN PANEL</b>\n\nChọn chức năng:",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin_deposits")
async def cb_admin_deposits(callback: CallbackQuery, session) -> None:
    if callback.from_user.id not in settings.ADMIN_IDS:
        await callback.answer("⛔ Không có quyền.", show_alert=True)
        return
    tx_repo = TransactionRepository(session)
    list_tx = await tx_repo.get_pending_deposits()
    if not list_tx:
        await callback.message.edit_text(
            "📥 Không có nạp chờ duyệt.",
            reply_markup=admin_main_keyboard(),
        )
        await callback.answer()
        return
    lines = []
    for tx in list_tx[:20]:
        lines.append(
            f"ID: {tx.id} | User: {tx.user_id} | "
            f"{format_currency(tx.amount)} | {tx.code}"
        )
    text = "📥 <b>NẠP CHỜ DUYỆT</b>\n\n" + "\n".join(lines)
    text += "\n\nDùng /approve &lt;id&gt; hoặc /reject &lt;id&gt; [lý do]"
    await callback.message.edit_text(
        text,
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "admin_withdraws")
async def cb_admin_withdraws(callback: CallbackQuery, session) -> None:
    if callback.from_user.id not in settings.ADMIN_IDS:
        await callback.answer("⛔ Không có quyền.", show_alert=True)
        return
    tx_repo = TransactionRepository(session)
    list_tx = await tx_repo.get_pending_withdraws()
    if not list_tx:
        await callback.message.edit_text(
            "📤 Không có rút chờ duyệt.",
            reply_markup=admin_main_keyboard(),
        )
        await callback.answer()
        return
    lines = []
    for tx in list_tx[:20]:
        lines.append(
            f"ID: {tx.id} | User: {tx.user_id} | "
            f"{format_currency(tx.amount)} | {tx.code}"
        )
    text = "📤 <b>RÚT CHỜ DUYỆT</b>\n\n" + "\n".join(lines)
    text += "\n\nDùng /approve &lt;id&gt; hoặc /reject &lt;id&gt; [lý do]"
    await callback.message.edit_text(
        text,
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(Command("approve"))
async def cmd_approve(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Dùng: /approve <transaction_id>")
        return
    try:
        tx_id = int(parts[1])
    except ValueError:
        await message.answer("ID phải là số.")
        return
    tx_repo = TransactionRepository(session)
    user_repo = UserRepository(session)
    log_repo = AdminLogRepository(session)
    tx = await tx_repo.get_by_id(tx_id)
    if not tx or tx.status != "pending":
        await message.answer("Giao dịch không tồn tại hoặc đã xử lý.")
        return
    tx = await tx_repo.approve(tx_id, message.from_user.id)
    if not tx:
        await message.answer("Đã xử lý hoặc không tìm thấy.")
        return
    if tx.type == "deposit":
        await user_repo.add_balance(tx.user_id, tx.amount)
        user = await user_repo.get_by_id(tx.user_id)
        if user:
            user.total_deposit += tx.amount
    else:
        user = await user_repo.get_by_id(tx.user_id)
        if user:
            user.total_withdraw += tx.amount
    await log_repo.log(
        message.from_user.id,
        "approve",
        target_id=tx_id,
        details=f"{tx.type} {tx.amount}",
    )
    await session.commit()
    await message.answer(f"✅ Đã duyệt giao dịch #{tx_id}.")


@router.message(Command("reject"))
async def cmd_reject(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.answer("Dùng: /reject <transaction_id> [lý do]")
        return
    try:
        tx_id = int(parts[1])
    except ValueError:
        await message.answer("ID phải là số.")
        return
    reason = parts[2].strip() if len(parts) > 2 else None
    tx_repo = TransactionRepository(session)
    user_repo = UserRepository(session)
    log_repo = AdminLogRepository(session)
    tx = await tx_repo.get_by_id(tx_id)
    if not tx or tx.status != "pending":
        await message.answer("Giao dịch không tồn tại hoặc đã xử lý.")
        return
    tx = await tx_repo.reject(tx_id, message.from_user.id, reason)
    if not tx:
        await message.answer("Đã xử lý hoặc không tìm thấy.")
        return
    if tx.type == "withdraw":
        await user_repo.add_balance(tx.user_id, tx.amount)
        u = await user_repo.get_by_id(tx.user_id)
        if u and u.withdraw_count_today > 0:
            u.withdraw_count_today -= 1
    await log_repo.log(
        message.from_user.id,
        "reject",
        target_id=tx_id,
        details=f"{tx.type} {reason or ''}",
    )
    await session.commit()
    await message.answer(f"❌ Đã từ chối giao dịch #{tx_id}.")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Dùng: /broadcast <nội dung>")
        return
    text = parts[1]
    result = await session.execute(select(User).where(User.is_banned == False))
    users = result.scalars().all()
    sent = 0
    for u in users:
        try:
            await message.bot.send_message(u.id, text, parse_mode="HTML")
            sent += 1
        except Exception:
            pass
    await message.answer(f"✅ Đã gửi cho {sent}/{len(users)} user.")


@router.message(Command("listusers"))
async def cmd_listusers(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    user_repo = UserRepository(session)
    total = await user_repo.count_all()
    await message.answer(f"👥 Tổng user: {total}")


@router.message(Command("check"))
async def cmd_check(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Dùng: /check <user_id>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("user_id phải là số.")
        return
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(uid)
    if not user:
        await message.answer("Không tìm thấy user.")
        return
    vip_repo = VIPRepository(session)
    vip = await vip_repo.get_by_level(user.vip_level)
    vip_name = vip.name if vip else "Đồng"
    text = (
        f"👤 User ID: {user.id}\n"
        f"Username: @{user.username or '-'}\n"
        f"Tên: {user.first_name}\n"
        f"Số dư: {format_currency(user.balance)}\n"
        f"Nạp: {format_currency(user.total_deposit)} | Rút: {format_currency(user.total_withdraw)}\n"
        f"Cược: {format_currency(user.total_wager)} | Lợi nhuận: {format_currency(user.total_profit)}\n"
        f"VIP: {vip_name} | Wager progress: {format_currency(user.wager_progress)}\n"
        f"Banned: {user.is_banned}"
    )
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Xem cược", callback_data=f"admin_show_bets_{uid}")]
    ])
    await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("admin_show_bets_"))
async def cb_admin_show_bets(callback: CallbackQuery, session) -> None:
    if callback.from_user.id not in settings.ADMIN_IDS:
        await callback.answer("⛔ Không có quyền.", show_alert=True)
        return
    uid = int(callback.data.replace("admin_show_bets_", ""))
    bet_repo = BetRepository(session)
    bets = await bet_repo.get_by_user(uid, limit=25)
    if not bets:
        await callback.answer("Không có cược.", show_alert=True)
        return
    lines = [f"User {uid} - {len(bets)} cược gần nhất:"]
    for b in bets[:15]:
        lines.append(f"{'✅' if b.won else '❌'} {b.choice} {format_currency(b.amount)} → {b.total} ({format_currency(b.profit)})")
    await callback.message.answer("\n".join(lines))
    await callback.answer()


@router.message(Command("createcoupon"))
async def cmd_createcoupon(message: Message, state: FSMContext, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 4:
        await message.answer(
            "Dùng: /createcoupon <code> <amount> <max_use>\n"
            "VD: /createcoupon ABC100 100000 10"
        )
        return
    code, amount_str, max_use_str = parts[1], parts[2], parts[3]
    try:
        amount = int(amount_str.replace(".", "").replace(",", ""))
        max_use = int(max_use_str)
    except ValueError:
        await message.answer("amount và max_use phải là số.")
        return
    coupon_repo = CouponRepository(session)
    try:
        c = await coupon_repo.create(code, amount, max_use, message.from_user.id)
        await session.commit()
        await message.answer(f"✅ Đã tạo coupon {c.code} | {format_currency(amount)} | max {max_use} lần.")
    except Exception as e:
        await message.answer(f"Lỗi: {e}")


@router.message(Command("deletecoupon"))
async def cmd_deletecoupon(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Dùng: /deletecoupon <code>")
        return
    code = parts[1].upper()
    coupon_repo = CouponRepository(session)
    ok = await coupon_repo.delete_by_code(code)
    await session.commit()
    await message.answer("✅ Đã xóa." if ok else "Không tìm thấy mã.")


@router.message(Command("couponinfo"))
async def cmd_couponinfo(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    coupon_repo = CouponRepository(session)
    coupons = await coupon_repo.get_all_active()
    if not coupons:
        await message.answer("Chưa có coupon nào.")
        return
    lines = []
    for c in coupons:
        lines.append(f"{c.code} | {format_currency(c.amount)} | {c.used_count}/{c.max_use}")
    await message.answer("Coupons:\n" + "\n".join(lines))


@router.message(Command("maintenance"))
async def cmd_maintenance(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Dùng: /maintenance on | off")
        return
    mode = parts[1].lower()
    if mode not in ("on", "off"):
        await message.answer("Dùng: /maintenance on | off")
        return
    # Store in bot data or env - simple approach: just reply. Real impl would use Redis or DB.
    await message.answer(f"Maintenance mode: {mode} (lưu ý: cần lưu state thật trong production)")


@router.message(Command("ban"))
async def cmd_ban(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Dùng: /ban <user_id>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("user_id phải là số.")
        return
    user_repo = UserRepository(session)
    await user_repo.set_banned(uid, True)
    log_repo = AdminLogRepository(session)
    await log_repo.log(message.from_user.id, "ban", target_id=uid, details=None)
    await session.commit()
    await message.answer(f"✅ Đã khóa user {uid}.")


@router.message(Command("unban"))
async def cmd_unban(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Dùng: /unban <user_id>")
        return
    try:
        uid = int(parts[1])
    except ValueError:
        await message.answer("user_id phải là số.")
        return
    user_repo = UserRepository(session)
    await user_repo.set_banned(uid, False)
    log_repo = AdminLogRepository(session)
    await log_repo.log(message.from_user.id, "unban", target_id=uid, details=None)
    await session.commit()
    await message.answer(f"✅ Đã mở khóa user {uid}.")


@router.message(Command("profit"))
async def cmd_profit(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    result = await session.execute(select(func.coalesce(func.sum(Bet.profit), 0)))
    total_profit = result.scalar() or 0
    await message.answer(f"📊 Tổng lợi nhuận (từ cược): {format_currency(int(total_profit))}")


@router.message(Command("today"))
async def cmd_today(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    result = await session.execute(
        select(func.coalesce(func.sum(Bet.profit), 0)).where(Bet.created_at >= today_start)
    )
    profit = result.scalar() or 0
    await message.answer(f"📊 Lợi nhuận hôm nay: {format_currency(int(profit))}")


@router.message(Command("weekly"))
async def cmd_weekly(message: Message, session) -> None:
    if message.from_user.id not in settings.ADMIN_IDS:
        return
    week_start = datetime.now(timezone.utc) - timedelta(days=7)
    result = await session.execute(
        select(func.coalesce(func.sum(Bet.profit), 0)).where(Bet.created_at >= week_start)
    )
    profit = result.scalar() or 0
    await message.answer(f"📊 Lợi nhuận 7 ngày: {format_currency(int(profit))}")
