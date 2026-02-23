from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.repositories import UserRepository, CouponRepository
from keyboards import main_menu_keyboard
from states import CouponStates
from utils import format_currency

router = Router(name="coupon")

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


@router.callback_query(F.data == "coupon")
async def cb_coupon(callback: CallbackQuery, state: FSMContext, session) -> None:
    await state.set_state(CouponStates.waiting_code)
    await callback.message.edit_text(
        "🎁 <b>ĐỔI MÃ COUPON</b>\n\n"
        "Gửi mã coupon (ví dụ: ABC123):",
        parse_mode="HTML",
    )
    await callback.answer()


@router.message(StateFilter(CouponStates.waiting_code), F.text)
async def msg_coupon_code(message: Message, state: FSMContext, session) -> None:
    code = (message.text or "").strip().upper()
    if not code:
        await message.answer("Vui lòng nhập mã.")
        return
    await state.clear()
    user_repo = UserRepository(session)
    coupon_repo = CouponRepository(session)
    user = await user_repo.get_by_id(message.from_user.id)
    if not user:
        await message.answer("Gửi /start trước.")
        return
    coupon = await coupon_repo.get_by_code(code)
    if not coupon:
        await message.answer(
            "❌ Mã không tồn tại hoặc đã hết hạn.",
            reply_markup=main_menu_keyboard(),
        )
        return
    if await coupon_repo.has_user_used(coupon.id, user.id):
        await message.answer(
            "❌ Bạn đã sử dụng mã này rồi.",
            reply_markup=main_menu_keyboard(),
        )
        return
    if coupon.used_count >= coupon.max_use:
        await message.answer(
            "❌ Mã đã hết lượt sử dụng.",
            reply_markup=main_menu_keyboard(),
        )
        return
    await coupon_repo.use_coupon(coupon.id, user.id)
    await coupon_repo.increment_used(coupon.id)
    await user_repo.add_balance(user.id, coupon.amount)
    await session.commit()
    await message.answer(
        f"✅ Đổi mã thành công! +{format_currency(coupon.amount)} đã được cộng vào ví.",
        reply_markup=main_menu_keyboard(),
    )
