from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Coupon, CouponUse


class CouponRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        code: str,
        amount: int,
        max_use: int,
        created_by: Optional[int] = None,
    ) -> Coupon:
        coupon = Coupon(
            code=code.upper(),
            amount=amount,
            max_use=max_use,
            created_by=created_by,
        )
        self.session.add(coupon)
        await self.session.flush()
        return coupon

    async def get_by_code(self, code: str) -> Optional[Coupon]:
        result = await self.session.execute(
            select(Coupon).where(
                Coupon.code == code.upper(),
                Coupon.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def use_coupon(self, coupon_id: int, user_id: int) -> bool:
        use = CouponUse(coupon_id=coupon_id, user_id=user_id)
        self.session.add(use)
        await self.session.flush()
        return True

    async def has_user_used(self, coupon_id: int, user_id: int) -> bool:
        result = await self.session.execute(
            select(CouponUse).where(
                CouponUse.coupon_id == coupon_id,
                CouponUse.user_id == user_id,
            )
        )
        return result.scalar_one_or_none() is not None

    async def increment_used(self, coupon_id: int) -> None:
        coupon = await self._get_by_id(coupon_id)
        if coupon:
            coupon.used_count += 1
            if coupon.used_count >= coupon.max_use:
                coupon.is_active = False
            await self.session.flush()

    async def _get_by_id(self, coupon_id: int) -> Optional[Coupon]:
        result = await self.session.execute(select(Coupon).where(Coupon.id == coupon_id))
        return result.scalar_one_or_none()

    async def get_all_active(self) -> List[Coupon]:
        result = await self.session.execute(
            select(Coupon).where(Coupon.is_active == True).order_by(Coupon.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete_by_code(self, code: str) -> bool:
        result = await self.session.execute(
            select(Coupon).where(Coupon.code == code.upper())
        )
        coupon = result.scalar_one_or_none()
        if not coupon:
            return False
        await self.session.delete(coupon)
        await self.session.flush()
        return True
