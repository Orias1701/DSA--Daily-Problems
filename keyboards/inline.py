from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings
from utils.formatters import format_currency


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🎲 Chơi Tài Xỉu", callback_data="game_taixiu"),
        InlineKeyboardButton(text="👤 Hồ sơ", callback_data="profile"),
    )
    builder.row(
        InlineKeyboardButton(text="💰 Nạp tiền", callback_data="deposit"),
        InlineKeyboardButton(text="📤 Rút tiền", callback_data="withdraw"),
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Mã coupon", callback_data="coupon"),
        InlineKeyboardButton(text="📞 Hỗ trợ", callback_data="support"),
    )
    return builder.as_markup()


def game_choice_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔴 Tài (11-18)", callback_data="bet_tai"),
        InlineKeyboardButton(text="🔵 Xỉu (3-10)", callback_data="bet_xiu"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Về menu", callback_data="main_menu"),
    )
    return builder.as_markup()


def bet_amount_keyboard() -> InlineKeyboardMarkup:
    amounts = [10_000, 50_000, 100_000, 500_000, 1_000_000]
    builder = InlineKeyboardBuilder()
    row = []
    for a in amounts:
        row.append(
            InlineKeyboardButton(
                text=format_currency(a),
                callback_data=f"amount_{a}",
            )
        )
    builder.row(*row)
    builder.row(
        InlineKeyboardButton(text="✏️ Nhập số khác", callback_data="amount_custom"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Hủy", callback_data="game_taixiu"),
    )
    return builder.as_markup()


def deposit_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📋 Hướng dẫn nạp", callback_data="deposit_help"),
        InlineKeyboardButton(text="💳 Tạo mã nạp", callback_data="deposit_create"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Về menu", callback_data="main_menu"),
    )
    return builder.as_markup()


def withdraw_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📤 Yêu cầu rút", callback_data="withdraw_create"),
        InlineKeyboardButton(text="🏦 Cập nhật TK", callback_data="withdraw_bank"),
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Về menu", callback_data="main_menu"),
    )
    return builder.as_markup()


def profile_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Lịch sử cược", callback_data="show_bets"),
        InlineKeyboardButton(text="◀️ Về menu", callback_data="main_menu"),
    )
    return builder.as_markup()


def support_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="💬 Mở ticket", callback_data="ticket_new"),
        InlineKeyboardButton(text="◀️ Về menu", callback_data="main_menu"),
    )
    return builder.as_markup()


def admin_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📥 Nạp chờ duyệt", callback_data="admin_deposits"),
        InlineKeyboardButton(text="📤 Rút chờ duyệt", callback_data="admin_withdraws"),
    )
    builder.row(
        InlineKeyboardButton(text="👥 Danh sách user", callback_data="admin_listusers"),
        InlineKeyboardButton(text="📊 Lợi nhuận", callback_data="admin_profit"),
    )
    builder.row(
        InlineKeyboardButton(text="🔧 Bảo trì", callback_data="admin_maintenance"),
    )
    return builder.as_markup()


def approve_reject_keyboard(
    tx_type: str,
    tx_id: int,
    disabled: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not disabled:
        builder.row(
            InlineKeyboardButton(
                text="✅ Duyệt",
                callback_data=f"admin_approve_{tx_type}_{tx_id}",
            ),
            InlineKeyboardButton(
                text="❌ Từ chối",
                callback_data=f"admin_reject_{tx_type}_{tx_id}",
            ),
        )
    return builder.as_markup()
