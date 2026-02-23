from aiogram.fsm.state import State, StatesGroup


class DepositStates(StatesGroup):
    entering_amount = State()
    waiting_transfer = State()


class WithdrawStates(StatesGroup):
    entering_amount = State()
    entering_bank_name = State()
    entering_bank_number = State()
    entering_bank_holder = State()


class GameStates(StatesGroup):
    choosing_side = State()
    choosing_amount = State()
    entering_amount = State()
    confirming_bet = State()


class SupportStates(StatesGroup):
    writing_message = State()


class CouponStates(StatesGroup):
    waiting_code = State()


class AdminStates(StatesGroup):
    broadcast_message = State()
    reject_reason = State()
    coupon_code = State()
    coupon_amount = State()
    coupon_max_use = State()
    maintenance_toggle = State()
    ban_user_id = State()
    check_user_id = State()
