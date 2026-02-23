import re
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import settings
from database.repositories import (
    UserRepository,
    BetRepository,
    VIPRepository,
)
from keyboards import (
    game_choice_keyboard,
    bet_amount_keyboard,
    main_menu_keyboard,
)
from states import GameStates
from services import GameService
from utils import format_currency

router = Router(name="game")

SEP = "━━━━━━━━━━━━━━━━━━━━━━"


@router.callback_query(F.data == "game_taixiu")
async def cb_game_taixiu(callback: CallbackQuery, state: FSMContext, session) -> None:
    await state.clear()
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(callback.from_user.id)
    if not user:
        await callback.answer("Gửi /start trước.")
        return
    if user.balance < settings.MIN_BET:
        await callback.message.edit_text(
            f"💰 Số dư không đủ. Tối thiểu cược: {format_currency(settings.MIN_BET)}\n\n"
            "💳 Vào <b>Nạp tiền</b> để nạp thêm.",
            parse_mode="HTML",
            reply_markup=main_menu_keyboard(),
        )
        await callback.answer()
        return
    await state.set_state(GameStates.choosing_side)
    await callback.message.edit_text(
        f"🎲 <b>TÀI XỈU</b>\n\n{SEP}\n"
        "🔴 <b>Tài</b>: Tổng 11 → 18\n"
        "🔵 <b>Xỉu</b>: Tổng 3 → 10\n"
        f"Cược: {format_currency(settings.MIN_BET)} - {format_currency(settings.MAX_BET)}\n{SEP}",
        reply_markup=game_choice_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.in_(["bet_tai", "bet_xiu"]))
async def cb_bet_side(callback: CallbackQuery, state: FSMContext, session) -> None:
    if (await state.get_state()) != GameStates.choosing_side.state:
        await callback.answer()
        return
    choice = "tai" if callback.data == "bet_tai" else "xiu"
    await state.update_data(choice=choice)
    await state.set_state(GameStates.choosing_amount)
    await callback.message.edit_text(
        "💰 Chọn số tiền cược:",
        reply_markup=bet_amount_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("amount_"))
async def cb_bet_amount(callback: CallbackQuery, state: FSMContext, session) -> None:
    if (await state.get_state()) != GameStates.choosing_amount.state:
        await callback.answer()
        return
    data = await state.get_data()
    choice = data.get("choice", "tai")
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(callback.from_user.id)
    if not user:
        await callback.answer("Lỗi.")
        return

    if callback.data == "amount_custom":
        await state.set_state(GameStates.entering_amount)
        await callback.message.edit_text(
            f"✏️ Nhập số tiền cược ({format_currency(settings.MIN_BET)} - {format_currency(settings.MAX_BET)}):"
        )
        await callback.answer()
        return

    amount_str = callback.data.replace("amount_", "")
    try:
        amount = int(amount_str)
    except ValueError:
        await callback.answer("Lỗi.")
        return

    if amount < settings.MIN_BET or amount > settings.MAX_BET:
        await callback.answer("Số tiền không hợp lệ.")
        return
    if user.balance < amount:
        await callback.answer("Số dư không đủ.")
        return

    await _place_bet(callback, session, state, user, choice, amount)
    await callback.answer()


@router.message(GameStates.entering_amount, F.text)
async def msg_bet_amount_custom(
    message: Message, state: FSMContext, session
) -> None:
    text = message.text.strip().replace(".", "").replace(",", "")
    if not re.match(r"^\d+$", text):
        await message.answer("Vui lòng nhập số nguyên dương.")
        return
    amount = int(text)
    if amount < settings.MIN_BET or amount > settings.MAX_BET:
        await message.answer(
            f"Số tiền phải từ {format_currency(settings.MIN_BET)} đến {format_currency(settings.MAX_BET)}."
        )
        return
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(message.from_user.id)
    if not user or user.balance < amount:
        await message.answer("Số dư không đủ.")
        await state.clear()
        return
    data = await state.get_data()
    choice = data.get("choice", "tai")
    await state.clear()
    await _place_bet_message(message, session, user, choice, amount)


async def _place_bet(
    callback: CallbackQuery, session, state: FSMContext, user, choice: str, amount: int
) -> None:
    await state.clear()
    user_repo = UserRepository(session)
    vip_repo = VIPRepository(session)
    bet_repo = BetRepository(session)
    multiplier = GameService.get_payout_multiplier(amount)
    ok = await user_repo.subtract_balance(user.id, amount)
    if not ok:
        await callback.message.edit_text(
            "Số dư không đủ.", reply_markup=main_menu_keyboard()
        )
        return
    d1 = await callback.message.answer_dice(emoji="🎲")
    dice1 = d1.dice.value
    d2 = await callback.message.answer_dice(emoji="🎲")
    dice2 = d2.dice.value
    d3 = await callback.message.answer_dice(emoji="🎲")
    dice3 = d3.dice.value
    total = dice1 + dice2 + dice3
    won = GameService.check_win(choice, total)
    profit = GameService.calculate_profit(amount, won, multiplier)
    new_vip = await vip_repo.get_level_for_wager(user.total_wager + amount)
    cashback_rate = settings.CASHBACK_RATE
    if new_vip > 0:
        v = await vip_repo.get_by_level(new_vip)
        if v:
            cashback_rate = v.cashback_rate
    cashback_earned = GameService.calculate_cashback(amount, cashback_rate)
    await user_repo.update_after_bet(
        user_id=user.id,
        profit=profit,
        wager=amount,
        won=won,
        cashback_earned=cashback_earned,
    )
    await user_repo.update_vip_from_wager(user.id, new_vip)
    await bet_repo.create(
        user_id=user.id,
        choice=choice,
        amount=amount,
        payout_multiplier=multiplier,
        dice1=dice1,
        dice2=dice2,
        dice3=dice3,
        total=total,
        won=won,
        profit=profit,
        cashback_earned=cashback_earned,
    )
    await session.commit()
    user = await user_repo.get_by_id(user.id)
    result_text = "🎉 THẮNG!" if won else "😔 Thua"
    await callback.message.answer(
        f"{SEP}\n{result_text}\n{SEP}\n"
        f"🎲 Xúc xắc: {dice1} + {dice2} + {dice3} = <b>{total}</b>\n"
        f"📊 Lựa chọn: {'Tài' if choice == 'tai' else 'Xỉu'}\n"
        f"💰 Tiền thưởng: {format_currency(profit + amount) if won else '0'}\n"
        f"💵 Lãi/Lỗ: {format_currency(profit)}\n"
        f"💎 Cashback: +{format_currency(cashback_earned)}\n{SEP}\n"
        f"💰 Số dư: <b>{format_currency(user.balance)}</b>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )


async def _place_bet_message(
    message: Message, session, user, choice: str, amount: int
) -> None:
    user_repo = UserRepository(session)
    vip_repo = VIPRepository(session)
    bet_repo = BetRepository(session)
    ok = await user_repo.subtract_balance(user.id, amount)
    if not ok:
        await message.answer("Số dư không đủ.", reply_markup=main_menu_keyboard())
        return
    multiplier = GameService.get_payout_multiplier(amount)
    d1 = await message.answer_dice(emoji="🎲")
    dice1 = d1.dice.value
    d2 = await message.answer_dice(emoji="🎲")
    dice2 = d2.dice.value
    d3 = await message.answer_dice(emoji="🎲")
    dice3 = d3.dice.value
    total = dice1 + dice2 + dice3
    won = GameService.check_win(choice, total)
    profit = GameService.calculate_profit(amount, won, multiplier)
    new_vip = await vip_repo.get_level_for_wager(user.total_wager + amount)
    cashback_rate = settings.CASHBACK_RATE
    if new_vip > 0:
        v = await vip_repo.get_by_level(new_vip)
        if v:
            cashback_rate = v.cashback_rate
    cashback_earned = GameService.calculate_cashback(amount, cashback_rate)
    await user_repo.update_after_bet(
        user_id=user.id,
        profit=profit,
        wager=amount,
        won=won,
        cashback_earned=cashback_earned,
    )
    await user_repo.update_vip_from_wager(user.id, new_vip)
    await bet_repo.create(
        user_id=user.id,
        choice=choice,
        amount=amount,
        payout_multiplier=multiplier,
        dice1=dice1,
        dice2=dice2,
        dice3=dice3,
        total=total,
        won=won,
        profit=profit,
        cashback_earned=cashback_earned,
    )
    await session.commit()
    user = await user_repo.get_by_id(user.id)
    result_text = "🎉 THẮNG!" if won else "😔 Thua"
    await message.answer(
        f"{SEP}\n{result_text}\n{SEP}\n"
        f"🎲 Xúc xắc: {dice1} + {dice2} + {dice3} = <b>{total}</b>\n"
        f"📊 Lựa chọn: {'Tài' if choice == 'tai' else 'Xỉu'}\n"
        f"💰 Tiền thưởng: {format_currency(profit + amount) if won else '0'}\n"
        f"💵 Lãi/Lỗ: {format_currency(profit)}\n"
        f"💎 Cashback: +{format_currency(cashback_earned)}\n{SEP}\n"
        f"💰 Số dư: <b>{format_currency(user.balance)}</b>",
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(),
    )
