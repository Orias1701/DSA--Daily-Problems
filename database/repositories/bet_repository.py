from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Bet


class BetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        choice: str,
        amount: int,
        payout_multiplier: float,
        dice1: int,
        dice2: int,
        dice3: int,
        total: int,
        won: bool,
        profit: int,
        cashback_earned: int = 0,
    ) -> Bet:
        bet = Bet(
            user_id=user_id,
            choice=choice,
            amount=amount,
            payout_multiplier=payout_multiplier,
            dice1=dice1,
            dice2=dice2,
            dice3=dice3,
            total=total,
            won=won,
            profit=profit,
            cashback_earned=cashback_earned,
        )
        self.session.add(bet)
        await self.session.flush()
        return bet

    async def get_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> List[Bet]:
        result = await self.session.execute(
            select(Bet)
            .where(Bet.user_id == user_id)
            .order_by(Bet.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_user_profit_today(self, user_id: int) -> Optional[int]:
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        result = await self.session.execute(
            select(func.coalesce(func.sum(Bet.profit), 0)).where(
                Bet.user_id == user_id,
                Bet.created_at >= today_start,
            )
        )
        return result.scalar() or 0
