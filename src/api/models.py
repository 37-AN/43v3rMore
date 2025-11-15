"""Pydantic models for API requests/responses."""

from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime


class SignalResponse(BaseModel):
    """Trading signal response."""

    id: UUID
    symbol: str
    action: str
    confidence: float
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward: Optional[float] = None
    timeframe: str
    reason: str
    created_at: datetime


class SignalListResponse(BaseModel):
    """List of signals response."""

    signals: List[SignalResponse]
    count: int
    timestamp: datetime


class UserCreate(BaseModel):
    """User registration request."""

    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    plan: str = "basic"


class UserResponse(BaseModel):
    """User data response."""

    id: UUID
    email: str
    name: Optional[str]
    plan: str
    status: str
    created_at: datetime


class SubscriptionCreate(BaseModel):
    """Subscription creation request."""

    plan: str = Field(..., description="Subscription plan")
    payment_method: Optional[str] = None


class SubscriptionResponse(BaseModel):
    """Subscription response."""

    id: UUID
    plan: str
    monthly_fee: float
    currency: str
    status: str
    next_billing_date: datetime
    created_at: datetime


class LoginRequest(BaseModel):
    """Login request."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    message: str
    details: Optional[Dict] = None


class AnalysisRequest(BaseModel):
    """Analysis request."""

    symbols: List[str] = Field(default_factory=list)
    timeframe: str = "H1"
    max_signals: Optional[int] = None


class AnalysisResponse(BaseModel):
    """Analysis response."""

    symbols_analyzed: int
    signals_generated: int
    signals: List[SignalResponse]
    timestamp: datetime
