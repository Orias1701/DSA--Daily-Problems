from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from database.models import AdminLog


class AdminLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(
        self,
        admin_id: int,
        action: str,
        target_id: Optional[int] = None,
        details: Optional[str] = None,
    ) -> None:
        log = AdminLog(
            admin_id=admin_id,
            action=action,
            target_id=target_id,
            details=details,
        )
        self.session.add(log)
        await self.session.flush()
