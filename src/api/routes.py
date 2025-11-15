"""API route definitions."""

from typing import List
from datetime import datetime, timezone, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from loguru import logger

from .models import (
    SignalResponse,
    SignalListResponse,
    UserCreate,
    UserResponse,
    SubscriptionCreate,
    SubscriptionResponse,
    AnalysisRequest,
    AnalysisResponse,
)
from .auth import get_current_active_user, require_plan
from ..database.models import User
from ..database.queries import UserQueries, SignalQueries, SubscriptionQueries
from ..quantum_engine import QuantumTradingEngine
from ..utils.config import get_settings

router = APIRouter(prefix="/api/v1")
settings = get_settings()


# Signals endpoints
@router.get("/signals", response_model=SignalListResponse)
async def get_signals(
    symbol: str = None,
    limit: int = 10,
    user: User = Depends(get_current_active_user),
):
    """
    Get recent trading signals.

    Args:
        symbol: Filter by symbol (optional)
        limit: Maximum signals to return
        user: Current authenticated user

    Returns:
        List of signals
    """
    try:
        queries = SignalQueries()
        signals = queries.get_recent_signals(symbol=symbol, limit=limit)

        signal_responses = [
            SignalResponse(
                id=s.id,
                symbol=s.symbol,
                action=s.action,
                confidence=s.confidence,
                entry_price=s.entry_price,
                stop_loss=s.stop_loss,
                take_profit=s.take_profit,
                risk_reward=s.risk_reward,
                timeframe=s.timeframe,
                reason=s.reason,
                created_at=s.created_at,
            )
            for s in signals
        ]

        return SignalListResponse(
            signals=signal_responses,
            count=len(signal_responses),
            timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.error(f"Get signals error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve signals",
        )


@router.get("/signals/{signal_id}", response_model=SignalResponse)
async def get_signal(
    signal_id: UUID,
    user: User = Depends(get_current_active_user),
):
    """Get specific signal by ID."""
    try:
        queries = SignalQueries()
        signal = queries.get_signal_by_id(signal_id)

        if not signal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Signal not found",
            )

        return SignalResponse(
            id=signal.id,
            symbol=signal.symbol,
            action=signal.action,
            confidence=signal.confidence,
            entry_price=signal.entry_price,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            risk_reward=signal.risk_reward,
            timeframe=signal.timeframe,
            reason=signal.reason,
            created_at=signal.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get signal error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve signal",
        )


# Analysis endpoint (premium feature)
@router.post("/analyze", response_model=AnalysisResponse)
async def run_analysis(
    request: AnalysisRequest,
    user: User = Depends(require_plan("pro")),
):
    """
    Run quantum analysis on symbols (Pro+ only).

    Args:
        request: Analysis parameters
        user: Current authenticated user (Pro+ plan)

    Returns:
        Analysis results with generated signals
    """
    try:
        logger.info(f"Analysis requested by {user.email}")

        symbols = request.symbols or settings.symbols_list
        engine = QuantumTradingEngine(symbols=symbols)

        with engine:
            results = engine.run_analysis_cycle(
                timeframe=request.timeframe,
                max_signals=request.max_signals,
            )

        signal_responses = [
            SignalResponse(**sig) for sig in results["signals"]
        ]

        return AnalysisResponse(
            symbols_analyzed=results["symbols_analyzed"],
            signals_generated=results["signals_generated"],
            signals=signal_responses,
            timestamp=datetime.fromisoformat(results["timestamp"]),
        )

    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analysis failed",
        )


# User endpoints
@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """
    Create new user account.

    Args:
        user_data: User registration data

    Returns:
        Created user
    """
    try:
        queries = UserQueries()

        # Check if user exists
        existing = queries.get_user_by_email(user_data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        # Create user
        user = queries.create_user(user_data.model_dump())

        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user",
            )

        logger.info(f"User created: {user.email}")

        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            plan=user.plan,
            status=user.status,
            created_at=user.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user",
        )


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        plan=user.plan,
        status=user.status,
        created_at=user.created_at,
    )


# Subscription endpoints
@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    user: User = Depends(get_current_active_user),
):
    """Create or upgrade subscription."""
    try:
        queries = SubscriptionQueries()

        # Check for existing subscription
        existing = queries.get_user_subscription(user.id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active subscription already exists",
            )

        # Get plan pricing
        plan_prices = {
            "basic": settings.basic_plan_price,
            "pro": settings.pro_plan_price,
            "premium": settings.premium_plan_price,
            "bot": settings.bot_license_price,
            "enterprise": settings.enterprise_price,
        }

        monthly_fee = plan_prices.get(subscription_data.plan, 500)

        # Create subscription
        sub_data = {
            "user_id": str(user.id),
            "plan": subscription_data.plan,
            "monthly_fee": monthly_fee,
            "currency": settings.currency,
            "status": "active",
            "current_period_start": datetime.now(timezone.utc).isoformat(),
            "current_period_end": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "next_billing_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            "payment_method": subscription_data.payment_method,
        }

        subscription = queries.create_subscription(sub_data)

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create subscription",
            )

        logger.info(f"Subscription created: {user.email} - {subscription_data.plan}")

        return SubscriptionResponse(
            id=subscription.id,
            plan=subscription.plan,
            monthly_fee=subscription.monthly_fee,
            currency=subscription.currency,
            status=subscription.status,
            next_billing_date=subscription.next_billing_date,
            created_at=subscription.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Subscription creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription",
        )


@router.get("/subscriptions/me", response_model=SubscriptionResponse)
async def get_my_subscription(user: User = Depends(get_current_active_user)):
    """Get current user's subscription."""
    try:
        queries = SubscriptionQueries()
        subscription = queries.get_user_subscription(user.id)

        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found",
            )

        return SubscriptionResponse(
            id=subscription.id,
            plan=subscription.plan,
            monthly_fee=subscription.monthly_fee,
            currency=subscription.currency,
            status=subscription.status,
            next_billing_date=subscription.next_billing_date,
            created_at=subscription.created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get subscription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve subscription",
        )
