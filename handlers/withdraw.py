import re
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import settings
from database.repositories import (
    UserRepository,
    TransactionRepository,
)
from keyboards import withdraw_keyboard, main_menu_keyboard
from states import WithdrawStates
from utils import format_currency

router = Router(name="withdraw")

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


@router.callback_query(F.data == "withdraw")
async def cb_withdraw(callback: CallbackQuery, session) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(callback.from_user.id)
    if not user:
        await callback.answer("Gửi /start trước.")
        return
    can_withdraw = user.wager_progress >= settings.WAGER_REQUIREMENT
    text = (
        "📤 <b>RÚT TIỀN</b>\n\n"
        f"💰 Số dư: {format_currency(user.balance)}\n"
        f"📊 Yêu cầu cược: {format_currency(settings.WAGER_REQUIREMENT)}\n"
        f"📈 Đã cược: {format_currency(user.wager_progress)}\n"
        f"📤 Rút hôm nay: {user.withdraw_count_today}/{settings.MAX_WITHDRAW_PER_DAY}\n\n"
    )
    if not can_withdraw:
        text += "⚠️ Bạn cần hoàn thành yêu cầu cược trước khi rút.\n"
    text += f"Rút tối thiểu: {format_currency(settings.MIN_WITHDRAW)}"
    await callback.message.edit_text(
        text,
        reply_markup=withdraw_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "withdraw_create")
async def cb_withdraw_create(
    callback: CallbackQuery, state: FSMContext, session
) -> None:
    user_repo = UserRepository(session)
    tx_repo = TransactionRepository(session)
    user = await user_repo.get_by_id(callback.from_user.id)
    if not user:
        await callback.answer("Lỗi.")
        return
    if user.wager_progress < settings.WAGER_REQUIREMENT:
        await callback.answer("Chưa đủ yêu cầu cược.", show_alert=True)
        return
    if user.withdraw_count_today >= settings.MAX_WITHDRAW_PER_DAY:
        await callback.answer("Đã hết lượt rút trong ngày.", show_alert=True)
        return
    if user.balance < settings.MIN_WITHDRAW:
        await callback.answer("Số dư không đủ.", show_alert=True)
        return
    pending = await tx_repo.get_pending_withdraw_by_user(callback.from_user.id)
    if pending:
        await callback.answer("Bạn đang có yêu cầu rút chờ duyệt.", show_alert=True)
        return
    if not user.bank_number or not user.bank_holder:
        await state.set_state(WithdrawStates.entering_bank_name)
        await callback.message.edit_text("🏦 Nhập tên ngân hàng:")
        await callback.answer()
        return
    await state.set_state(WithdrawStates.entering_amount)
    await callback.message.edit_text(
        f"✏️ Nhập số tiền rút (tối thiểu {format_currency(settings.MIN_WITHDRAW)}):"
    )
    await callback.answer()


@router.callback_query(F.data == "withdraw_bank")
async def cb_withdraw_bank(
    callback: CallbackQuery, state: FSMContext, session
) -> None:
    await state.set_state(WithdrawStates.entering_bank_name)
    await callback.message.edit_text("🏦 Nhập tên ngân hàng:")
    await callback.answer()


@router.message(WithdrawStates.entering_bank_name, F.text)
async def msg_bank_name(message: Message, state: FSMContext, session) -> None:
    await state.update_data(bank_name=message.text.strip())
    await state.set_state(WithdrawStates.entering_bank_number)
    await message.answer("📌 Nhập số tài khoản:")


@router.message(WithdrawStates.entering_bank_number, F.text)
async def msg_bank_number(message: Message, state: FSMContext, session) -> None:
    await state.update_data(bank_number=message.text.strip())
    await state.set_state(WithdrawStates.entering_bank_holder)
    await message.answer("👤 Nhập tên chủ tài khoản:")


@router.message(WithdrawStates.entering_bank_holder, F.text)
async def msg_bank_holder(message: Message, state: FSMContext, session) -> None:
    await state.update_data(bank_holder=message.text.strip())
    data = await state.get_data()
    user_repo = UserRepository(session)
    await user_repo.update_bank_info(
        message.from_user.id,
        data["bank_name"],
        data["bank_number"],
        data["bank_holder"],
    )
    await session.commit()
    await state.clear()
    await message.answer(
        "✅ Đã lưu thông tin ngân hàng.\n"
        "Bạn có thể tạo yêu cầu rút từ menu Rút tiền.",
        reply_markup=main_menu_keyboard(),
    )


@router.message(WithdrawStates.entering_amount, F.text)
async def msg_withdraw_amount(
    message: Message, state: FSMContext, session
) -> None:
    text = message.text.strip().replace(".", "").replace(",", "")
    if not re.match(r"^\d+$", text):
        await message.answer("Vui lòng nhập số nguyên.")
        return
    amount = int(text)
    if amount < settings.MIN_WITHDRAW:
        await message.answer(
            f"Số tiền tối thiểu {format_currency(settings.MIN_WITHDRAW)}."
        )
        return
    user_repo = UserRepository(session)
    tx_repo = TransactionRepository(session)
    user = await user_repo.get_by_id(message.from_user.id)
    if not user or user.balance < amount:
        await message.answer("Số dư không đủ.")
        await state.clear()
        return
    if user.withdraw_count_today >= settings.MAX_WITHDRAW_PER_DAY:
        await message.answer("Đã hết lượt rút trong ngày.")
        await state.clear()
        return
    code = tx_repo.generate_withdraw_code()
    tx = await tx_repo.create_withdraw(
        user_id=message.from_user.id,
        amount=amount,
        code=code,
        bank_name=user.bank_name or "",
        bank_number=user.bank_number or "",
        bank_holder=user.bank_holder or "",
    )
    ok = await user_repo.subtract_balance(user.id, amount)
    if not ok:
        await message.answer("Lỗi. Thử lại sau.")
        await state.clear()
        return
    await user_repo.increment_withdraw_count(user.id)
    await session.commit()
    await state.clear()
    await message.answer(
        f"✅ <b>YÊU CẦU RÚT</b>\n\n{SEP}\n"
        f"Mã: <b>{code}</b>\n"
        f"Số tiền: {format_currency(amount)}\n"
        f"Trạng thái: ⏳ Chờ duyệt\n{SEP}\n"
        "Admin sẽ xử lý trong thời gian sớm nhất.",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )
