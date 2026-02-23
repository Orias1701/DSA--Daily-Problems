from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Ticket, TicketMessage


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_open_ticket_by_user(self, user_id: int) -> Optional[Ticket]:
        result = await self.session.execute(
            select(Ticket).where(
                and_(
                    Ticket.user_id == user_id,
                    Ticket.is_open == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int) -> Ticket:
        ticket = Ticket(user_id=user_id)
        self.session.add(ticket)
        await self.session.flush()
        return ticket

    async def add_message(
        self,
        ticket_id: int,
        is_from_user: bool,
        text: str,
    ) -> TicketMessage:
        msg = TicketMessage(
            ticket_id=ticket_id,
            is_from_user=is_from_user,
            text=text,
        )
        self.session.add(msg)
        await self.session.flush()
        ticket = await self._get_by_id(ticket_id)
        if ticket:
            ticket.last_activity = datetime.utcnow()
        await self.session.flush()
        return msg

    async def close_ticket(self, ticket_id: int) -> None:
        result = await self.session.execute(select(Ticket).where(Ticket.id == ticket_id))
        ticket = result.scalar_one_or_none()
        if ticket:
            ticket.is_open = False
            await self.session.flush()

    async def _get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        result = await self.session.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        return await self._get_by_id(ticket_id)

    async def get_stale_tickets(self, inactivity_minutes: int) -> List[Ticket]:
        threshold = datetime.utcnow() - timedelta(minutes=inactivity_minutes)
        result = await self.session.execute(
            select(Ticket).where(
                and_(
                    Ticket.is_open == True,
                    Ticket.last_activity < threshold,
                )
            )
        )
        return list(result.scalars().all())
