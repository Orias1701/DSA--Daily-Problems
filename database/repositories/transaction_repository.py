import secrets
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Transaction


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def generate_deposit_code(self) -> str:
        return "NAP" + secrets.token_hex(3).upper()[:6]

    def generate_withdraw_code(self) -> str:
        return "W" + secrets.token_hex(3).upper()[:6]

    async def create_deposit(
        self,
        user_id: int,
        amount: int,
        code: str,
    ) -> Transaction:
        tx = Transaction(
            user_id=user_id,
            type="deposit",
            amount=amount,
            status="pending",
            code=code,
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def create_withdraw(
        self,
        user_id: int,
        amount: int,
        code: str,
        bank_name: str,
        bank_number: str,
        bank_holder: str,
    ) -> Transaction:
        tx = Transaction(
            user_id=user_id,
            type="withdraw",
            amount=amount,
            status="pending",
            code=code,
            bank_name=bank_name,
            bank_number=bank_number,
            bank_holder=bank_holder,
        )
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def get_by_code(self, code: str) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(Transaction.code == code)
        )
        return result.scalar_one_or_none()

    async def get_pending_deposit_by_user(self, user_id: int) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "deposit",
                    Transaction.status == "pending",
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_pending_withdraw_by_user(self, user_id: int) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.type == "withdraw",
                    Transaction.status == "pending",
                )
            )
        )
        return result.scalar_one_or_none()

    async def approve(
        self,
        transaction_id: int,
        processed_by: int,
    ) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.status == "pending",
            )
        )
        tx = result.scalar_one_or_none()
        if not tx:
            return None
        tx.status = "approved"
        tx.processed_at = datetime.utcnow()
        tx.processed_by = processed_by
        await self.session.flush()
        return tx

    async def reject(
        self,
        transaction_id: int,
        processed_by: int,
        reason: Optional[str] = None,
    ) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.status == "pending",
            )
        )
        tx = result.scalar_one_or_none()
        if not tx:
            return None
        tx.status = "rejected"
        tx.processed_at = datetime.utcnow()
        tx.processed_by = processed_by
        tx.reject_reason = reason
        await self.session.flush()
        return tx

    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def get_pending_deposits(self) -> List[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.type == "deposit",
                    Transaction.status == "pending",
                )
            ).order_by(Transaction.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_pending_withdraws(self) -> List[Transaction]:
        result = await self.session.execute(
            select(Transaction).where(
                and_(
                    Transaction.type == "withdraw",
                    Transaction.status == "pending",
                )
            ).order_by(Transaction.created_at.desc())
        )
        return list(result.scalars().all())
