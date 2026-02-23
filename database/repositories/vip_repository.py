from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import VIPLevel


class VIPRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_level(self, level: int) -> Optional[VIPLevel]:
        result = await self.session.execute(
            select(VIPLevel).where(VIPLevel.level == level)
        )
        return result.scalar_one_or_none()

    async def get_level_for_wager(self, total_wager: int) -> int:
        result = await self.session.execute(
            select(VIPLevel)
            .where(VIPLevel.min_total_wager <= total_wager)
            .order_by(VIPLevel.min_total_wager.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row.level if row else 0

    async def get_all(self) -> List[VIPLevel]:
        result = await self.session.execute(
            select(VIPLevel).order_by(VIPLevel.level.asc())
        )
        return list(result.scalars().all())

    async def ensure_default_levels(self) -> None:
        existing = await self.get_all()
        if existing:
            return
        defaults = [
            (0, 0, "Đồng", 0.005),
            (1, 1_000_000, "Bạc", 0.006),
            (2, 5_000_000, "Vàng", 0.007),
            (3, 20_000_000, "Bạch Kim", 0.008),
            (4, 50_000_000, "Kim Cương", 0.01),
        ]
        for level, min_wager, name, rate in defaults:
            vip = VIPLevel(
                level=level,
                min_total_wager=min_wager,
                name=name,
                cashback_rate=rate,
            )
            self.session.add(vip)
        await self.session.flush()
