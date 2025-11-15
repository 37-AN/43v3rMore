"""Database models using Pydantic."""

from typing import Optional, Dict, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID, uuid4


class User(BaseModel):
    """User account model."""

    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    plan: str = "basic"  # basic, pro, premium, bot, enterprise
    status: str = "active"  # active, paused, cancelled, trial
    telegram_id: Optional[str] = None
    whatsapp_number: Optional[str] = None
    preferences: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "trader@example.com",
                "name": "John Trader",
                "plan": "pro",
                "status": "active",
                "telegram_id": "123456789",
            }
        }


class Subscription(BaseModel):
    """Subscription model."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    plan: str
    monthly_fee: float
    currency: str = "ZAR"
    status: str = "active"  # active, paused, cancelled, past_due
    trial_end: Optional[datetime] = None
    current_period_start: datetime = Field(default_factory=datetime.utcnow)
    current_period_end: datetime
    cancel_at_period_end: bool = False
    payment_method: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    next_billing_date: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "plan": "pro",
                "monthly_fee": 1000.0,
                "currency": "ZAR",
                "status": "active",
            }
        }


class Signal(BaseModel):
    """Trading signal model."""

    id: UUID = Field(default_factory=uuid4)
    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward: Optional[float] = None
    timeframe: str = "H1"
    reason: str = ""
    metadata: Dict = Field(default_factory=dict)
    status: str = "pending"  # pending, executed, hit_tp, hit_sl, expired
    result_pnl: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "EURUSD",
                "action": "BUY",
                "confidence": 0.87,
                "entry_price": 1.1000,
                "stop_loss": 1.0950,
                "take_profit": 1.1100,
                "timeframe": "H1",
            }
        }


class SignalDelivery(BaseModel):
    """Signal delivery tracking."""

    id: UUID = Field(default_factory=uuid4)
    signal_id: UUID
    user_id: UUID
    channel: str  # telegram, whatsapp, email, sms
    status: str  # pending, sent, delivered, failed
    error_message: Optional[str] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsEvent(BaseModel):
    """Analytics event tracking."""

    id: UUID = Field(default_factory=uuid4)
    event_type: str  # signal_generated, signal_delivered, user_signup, subscription_created, etc.
    user_id: Optional[UUID] = None
    data: Dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "signal_generated",
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "data": {"symbol": "EURUSD", "action": "BUY", "confidence": 0.87},
            }
        }


class Payment(BaseModel):
    """Payment transaction model."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    subscription_id: Optional[UUID] = None
    amount: float
    currency: str = "ZAR"
    status: str  # pending, completed, failed, refunded
    payment_method: str  # payfast, eft, card
    transaction_id: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None


class LeadScore(BaseModel):
    """Lead qualification score."""

    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: Optional[str] = None
    source: str  # website, referral, ad, etc.
    score: int = 0  # 0-100
    stage: str = "new"  # new, contacted, qualified, converted, lost
    interests: List[str] = Field(default_factory=list)
    notes: str = ""
    metadata: Dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
