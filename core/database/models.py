from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from typing import List, Optional

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    language_code = Column(String, default='ru')
    referral_balance = Column(Integer, default=0)
    l2_referral_balance = Column(Integer, default=0)
    referrer_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=True)
    referral_code = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=func.now())
    trial_used = Column(Boolean, default=False, nullable=False)
    activated_first_vpn = Column(Boolean, default=False, nullable=False)
    unassigned_days = Column(Integer, default=0)
    bonus_days = Column(Integer, default=0)
    total_paid_out = Column(Integer, default=0)
    is_banned = Column(Boolean, default=False, nullable=False, server_default='f')

    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username='{self.username}')>"


class Server(Base):
    __tablename__ = 'servers'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    api_url = Column(String, nullable=False)
    api_user = Column(String, nullable=False)
    api_password = Column(String, nullable=False)
    inbound_id = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Server(id={self.id}, name='{self.name}')>"


class Tariff(Base):
    __tablename__ = 'tariffs'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    name = Column(JSON, nullable=False)
    duration_days = Column(Integer, nullable=False)
    price_rub = Column(Integer, nullable=False)
    price_stars = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Tariff(id={self.id}, name='{self.name}')>"


class Subscription(Base):
    __tablename__ = 'subscriptions'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    server_id = Column(Integer, ForeignKey('servers.id'), nullable=False)
    xui_user_uuid = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    user: Mapped["User"] = relationship(back_populates="subscriptions")

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, server_id={self.server_id})>"


class Transaction(Base):
    __tablename__ = 'transactions'
    __table_args__ = {'extend_existing': True}

    id = Column(String, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    tariff_id = Column(Integer, ForeignKey('tariffs.id'), nullable=True)
    amount = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)
    payment_system = Column(String, nullable=False)
    status = Column(String, nullable=False)
    payment_details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, amount={self.amount}, status='{self.status}')>"

class GiftCode(Base):
    __tablename__ = 'gift_codes'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    tariff_id = Column(Integer, ForeignKey('tariffs.id'), nullable=False)
    buyer_user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False)
    is_activated = Column(Boolean, default=False, nullable=False)
    activated_by_user_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=True)
    created_at = Column(DateTime, default=func.now())
    activated_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<GiftCode(id={self.id}, code='{self.code}', buyer_user_id={self.buyer_user_id})>"