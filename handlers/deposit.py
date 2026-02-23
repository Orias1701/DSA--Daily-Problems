import re
from urllib.parse import quote
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import settings
from database.repositories import (
    UserRepository,
    TransactionRepository,
)
from keyboards import deposit_keyboard, main_menu_keyboard
from states import DepositStates
from services import BankService
from utils import format_currency

router = Router(name="deposit")

SEP = "━━━━━━━━━━━━━━━━━━━━━━"

def _build_vietqr_image_url(amount: int, add_info: str) -> str | None:
    """
    Tạo URL ảnh VietQR (img.vietqr.io). Trả None nếu thiếu cấu hình.
    Yêu cầu: ADMIN_BANK_BIN + ADMIN_BANK_NUMBER.
    """
    bank_bin = (settings.ADMIN_BANK_BIN or "").strip()
    account_no = (settings.ADMIN_BANK_NUMBER or "").strip()
    if not bank_bin or not account_no:
        return None
    template = (settings.VIETQR_TEMPLATE or "compact2").strip()
    add_info_q = quote(add_info, safe="")
    account_name_q = quote(settings.ADMIN_BANK_HOLDER or "", safe="")
    return (
        f"https://img.vietqr.io/image/{bank_bin}-{account_no}-{template}.png"
        f"?amount={amount}&addInfo={add_info_q}&accountName={account_name_q}"
    )


@router.callback_query(F.data == "deposit")
async def cb_deposit(callback: CallbackQuery, session) -> None:
    await callback.message.edit_text(
        "💰 <b>NẠP TIỀN</b>\n\n"
        "Chọn hành động bên dưới.",
        reply_markup=deposit_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "deposit_help")
async def cb_deposit_help(callback: CallbackQuery, session) -> None:
    text = (
        f"📋 <b>HƯỚNG DẪN NẠP TIỀN</b>\n\n{SEP}\n"
        f"🏦 Ngân hàng: <b>{settings.ADMIN_BANK_NAME}</b>\n"
        f"📌 Số TK: <b>{settings.ADMIN_BANK_NUMBER}</b>\n"
        f"👤 Chủ TK: <b>{settings.ADMIN_BANK_HOLDER}</b>\n{SEP}\n"
        "1️⃣ Chọn <b>Tạo mã nạp</b>\n"
        "2️⃣ Chuyển <b>đúng số tiền</b>\n"
        "3️⃣ Nội dung chuyển khoản: <b>đúng mã</b> (NAP...)\n"
        "4️⃣ Hệ thống sẽ duyệt (tự động nếu dùng Bank API)\n\n"
        "💡 Nếu đã cấu hình VietQR, bot sẽ gửi <b>ảnh QR</b> để quét thanh toán."
    )
    await callback.message.edit_text(
        text,
        reply_markup=deposit_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "deposit_create")
async def cb_deposit_create(
    callback: CallbackQuery, state: FSMContext, session
) -> None:
    tx_repo = TransactionRepository(session)
    pending = await tx_repo.get_pending_deposit_by_user(callback.from_user.id)
    if pending:
        await callback.message.edit_text(
            f"⏳ Bạn đang có giao dịch chờ duyệt: <b>{pending.code}</b>\n"
            f"Số tiền: {format_currency(pending.amount)}\n\n"
            "Vui lòng chờ duyệt hoặc hủy trước khi tạo mã mới.",
            reply_markup=deposit_keyboard(),
            parse_mode="HTML",
        )
        await callback.answer()
        return
    await state.set_state(DepositStates.entering_amount)
    await callback.message.edit_text(
        "✏️ Nhập số tiền cần nạp (VNĐ):"
    )
    await callback.answer()


@router.message(DepositStates.entering_amount, F.text)
async def msg_deposit_amount(
    message: Message, state: FSMContext, session
) -> None:
    text = message.text.strip().replace(".", "").replace(",", "")
    if not re.match(r"^\d+$", text):
        await message.answer("Vui lòng nhập số nguyên dương.")
        return
    amount = int(text)
    if amount < settings.MIN_DEPOSIT:
        await message.answer(
            f"Số tiền tối thiểu {format_currency(settings.MIN_DEPOSIT)} VNĐ."
        )
        return
    tx_repo = TransactionRepository(session)
    code = tx_repo.generate_deposit_code()
    while await tx_repo.get_by_code(code):
        code = tx_repo.generate_deposit_code()
    await tx_repo.create_deposit(
        user_id=message.from_user.id,
        amount=amount,
        code=code,
    )
    await session.commit()
    await state.clear()
    body = (
        f"✅ <b>MÃ NẠP TIỀN</b>\n\n{SEP}\n"
        f"💰 Số tiền: <b>{format_currency(amount)}</b> VNĐ\n"
        f"📌 Nội dung CK: <b>{code}</b>\n{SEP}\n"
        f"🏦 {settings.ADMIN_BANK_NAME}\n"
        f"📌 Số TK: <b>{settings.ADMIN_BANK_NUMBER}</b>\n"
        f"👤 {settings.ADMIN_BANK_HOLDER}\n{SEP}\n"
        "Chuyển <b>đúng số tiền</b> và <b>đúng nội dung</b>.\n"
        "Giao dịch sẽ được duyệt khi hệ thống xác nhận."
    )
    await message.answer(body, parse_mode="HTML", reply_markup=main_menu_keyboard())

    qr_url = _build_vietqr_image_url(amount=amount, add_info=code)
    if qr_url:
        await message.answer_photo(
            photo=qr_url,
            caption=(
                f"📲 <b>QR THANH TOÁN</b>\n\n{SEP}\n"
                f"💰 Số tiền: <b>{format_currency(amount)}</b> VNĐ\n"
                f"📌 Nội dung: <b>{code}</b>\n{SEP}\n"
                "Quét QR và chuyển <b>đúng số tiền</b> + <b>đúng nội dung</b> nhé."
            ),
            parse_mode="HTML",
        )

    bank = BankService()
    if bank.enabled and bank.base_url:
        match, _ = await bank.check_transaction(amount, code)
        if match:
            from database import async_session_maker
            from database.models import User
            from sqlalchemy import update

            async with async_session_maker() as auto_session:
                tx_repo2 = TransactionRepository(auto_session)
                user_repo2 = UserRepository(auto_session)
                tx = await tx_repo2.get_by_code(code)
                if tx and tx.status == "pending":
                    await tx_repo2.approve(tx.id, 0)
                    await user_repo2.add_balance(tx.user_id, tx.amount)
                    await auto_session.execute(
                        update(User)
                        .where(User.id == tx.user_id)
                        .values(total_deposit=User.total_deposit + tx.amount)
                    )
                    await auto_session.commit()
                    await message.answer(
                        "🎉 Giao dịch đã được xác nhận tự động. Số dư đã cập nhật.",
                        reply_markup=main_menu_keyboard(),
                    )
