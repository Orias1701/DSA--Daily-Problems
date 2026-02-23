from datetime import datetime, timedelta
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import settings
from database.repositories import TicketRepository
from keyboards import support_keyboard, main_menu_keyboard
from states import SupportStates

router = Router(name="support")

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


@router.callback_query(F.data == "support")
async def cb_support(callback: CallbackQuery, session) -> None:
    await callback.message.edit_text(
        "📞 <b>HỖ TRỢ</b>\n\n"
        "Mở ticket để nhắn tin với admin (ẩn danh).\n"
        "Ticket tự đóng sau 10 phút không hoạt động.",
        reply_markup=support_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "ticket_new")
async def cb_ticket_new(
    callback: CallbackQuery, state: FSMContext, session
) -> None:
    ticket_repo = TicketRepository(session)
    existing = await ticket_repo.get_open_ticket_by_user(callback.from_user.id)
    if existing:
        await callback.message.edit_text(
            "Bạn đang có ticket mở. Vui lòng gửi nội dung nhắn tại đây.\n"
            "Gửi /cancel để đóng ticket.",
            reply_markup=main_menu_keyboard(),
        )
        await state.set_state(SupportStates.writing_message)
        await state.update_data(ticket_id=existing.id)
        await callback.answer()
        return
    ticket = await ticket_repo.create(callback.from_user.id)
    await session.commit()
    await state.set_state(SupportStates.writing_message)
    await state.update_data(ticket_id=ticket.id)
    await callback.message.edit_text(
        "✅ Ticket đã mở. Gửi nội dung cần hỗ trợ.\nGửi /cancel để đóng.",
        reply_markup=main_menu_keyboard(),
    )
    await callback.answer()


@router.message(StateFilter(SupportStates.writing_message), F.text)
async def msg_ticket_message(
    message: Message, state: FSMContext, session
) -> None:
    if message.text and message.text.strip() == "/cancel":
        data = await state.get_data()
        ticket_id = data.get("ticket_id")
        if ticket_id:
            ticket_repo = TicketRepository(session)
            await ticket_repo.close_ticket(ticket_id)
            await session.commit()
        await state.clear()
        await message.answer("Ticket đã đóng.", reply_markup=main_menu_keyboard())
        return
    data = await state.get_data()
    ticket_id = data.get("ticket_id")
    if not ticket_id:
        await state.clear()
        return
    ticket_repo = TicketRepository(session)
    await ticket_repo.add_message(ticket_id, is_from_user=True, text=message.text or "")
    await session.commit()
    await message.answer(
        "✅ Đã gửi. Admin sẽ phản hồi sớm. Gửi /cancel để đóng ticket."
    )
