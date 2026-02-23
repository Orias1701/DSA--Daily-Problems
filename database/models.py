from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), default="")
    balance: Mapped[int] = mapped_column(BigInteger, default=0)
    total_deposit: Mapped[int] = mapped_column(BigInteger, default=0)
    total_withdraw: Mapped[int] = mapped_column(BigInteger, default=0)
    total_wager: Mapped[int] = mapped_column(BigInteger, default=0)
    total_profit: Mapped[int] = mapped_column(BigInteger, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    wager_progress: Mapped[int] = mapped_column(BigInteger, default=0)
    cashback_today: Mapped[int] = mapped_column(BigInteger, default=0)
    daily_wager: Mapped[int] = mapped_column(BigInteger, default=0)
    withdraw_count_today: Mapped[int] = mapped_column(Integer, default=0)
    vip_level: Mapped[int] = mapped_column(Integer, default=0)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    welcome_bonus_given: Mapped[bool] = mapped_column(Boolean, default=False)
    bank_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bank_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bank_holder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_cashback_reset: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    last_withdraw_reset: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", back_populates="user", foreign_keys="Transaction.user_id"
    )
    bets: Mapped[List["Bet"]] = relationship("Bet", back_populates="user")
    coupon_uses: Mapped[List["CouponUse"]] = relationship(
        "CouponUse", back_populates="user"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(20))
    amount: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    reject_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bank_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bank_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bank_holder: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    processed_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    user: Mapped["User"] = relationship(
        "User", back_populates="transactions", foreign_keys=[user_id]
    )


class Bet(Base):
    __tablename__ = "bets"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    choice: Mapped[str] = mapped_column(String(10))
    amount: Mapped[int] = mapped_column(BigInteger)
    payout_multiplier: Mapped[float] = mapped_column(Float)
    dice1: Mapped[int] = mapped_column(Integer)
    dice2: Mapped[int] = mapped_column(Integer)
    dice3: Mapped[int] = mapped_column(Integer)
    total: Mapped[int] = mapped_column(Integer)
    won: Mapped[bool] = mapped_column(Boolean)
    profit: Mapped[int] = mapped_column(BigInteger)
    cashback_earned: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="bets")


class VIPLevel(Base):
    __tablename__ = "vip_levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    level: Mapped[int] = mapped_column(Integer, unique=True)
    min_total_wager: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(50))
    cashback_rate: Mapped[float] = mapped_column(Float, default=0.005)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True)
    amount: Mapped[int] = mapped_column(BigInteger)
    max_use: Mapped[int] = mapped_column(Integer)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    uses: Mapped[List["CouponUse"]] = relationship("CouponUse", back_populates="coupon")


class CouponUse(Base):
    __tablename__ = "coupon_uses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    coupon_id: Mapped[int] = mapped_column(Integer, ForeignKey("coupons.id"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    coupon: Mapped["Coupon"] = relationship("Coupon", back_populates="uses")
    user: Mapped["User"] = relationship("User", back_populates="coupon_uses")

    __table_args__ = (UniqueConstraint("coupon_id", "user_id", name="uq_coupon_user"),)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    messages: Mapped[List["TicketMessage"]] = relationship(
        "TicketMessage", back_populates="ticket"
    )


class TicketMessage(Base):
    __tablename__ = "ticket_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.id"))
    is_from_user: Mapped[bool] = mapped_column(Boolean)
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    ticket: Mapped["Ticket"] = relationship("Ticket", back_populates="messages")


class AdminLog(Base):
    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    admin_id: Mapped[int] = mapped_column(BigInteger)
    action: Mapped[str] = mapped_column(String(100))
    target_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
