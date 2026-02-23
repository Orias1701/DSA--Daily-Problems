from datetime import datetime, date
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        user_id: int,
        username: Optional[str] = None,
        first_name: str = "",
    ) -> User:
        user = await self.get_by_id(user_id)
        if user:
            if username is not None:
                user.username = username
            if first_name:
                user.first_name = first_name
            return user
        user = User(
            id=user_id,
            username=username,
            first_name=first_name or "User",
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def add_balance(self, user_id: int, amount: int) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(balance=User.balance + amount)
        )

    async def subtract_balance(self, user_id: int, amount: int) -> bool:
        result = await self.session.execute(
            update(User)
            .where(User.id == user_id, User.balance >= amount)
            .values(balance=User.balance - amount)
        )
        return result.rowcount > 0

    async def update_after_bet(
        self,
        user_id: int,
        profit: int,
        wager: int,
        won: bool,
        cashback_earned: int,
    ) -> None:
        user = await self.get_by_id(user_id)
        if not user:
            return
        user.balance += profit
        user.total_wager += wager
        user.wager_progress += wager
        user.daily_wager += wager
        user.total_profit += profit
        user.cashback_today += cashback_earned
        if won:
            user.wins += 1
        else:
            user.losses += 1
        await self.session.flush()

    async def update_vip_from_wager(self, user_id: int, vip_level: int) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(vip_level=vip_level)
        )

    async def reset_daily_wager_and_cashback(self, user_id: int) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                daily_wager=0,
                cashback_today=0,
                last_cashback_reset=datetime.utcnow(),
            )
        )

    async def reset_withdraw_count(self, user_id: int) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                withdraw_count_today=0,
                last_withdraw_reset=datetime.utcnow(),
            )
        )

    async def increment_withdraw_count(self, user_id: int) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(withdraw_count_today=User.withdraw_count_today + 1)
        )

    async def update_bank_info(
        self,
        user_id: int,
        bank_name: str,
        bank_number: str,
        bank_holder: str,
    ) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                bank_name=bank_name,
                bank_number=bank_number,
                bank_holder=bank_holder,
            )
        )

    async def set_banned(self, user_id: int, banned: bool) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(is_banned=banned)
        )

    async def count_all(self) -> int:
        result = await self.session.execute(select(User))
        return len(result.scalars().all())
