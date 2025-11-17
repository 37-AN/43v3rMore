"""Dashboard API routes for admin monitoring and management."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from uuid import UUID
from loguru import logger

from .auth import get_current_active_user, require_plan
from ..database.models import User
from ..database.queries import UserQueries, SignalQueries, SubscriptionQueries
from ..utils.config import get_settings

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])
settings = get_settings()


# Response Models
class ServiceHealthResponse(BaseModel):
    name: str
    status: str  # healthy, degraded, down
    last_check: Optional[str] = None
    response_time: Optional[int] = None


class DashboardOverviewResponse(BaseModel):
    active_users: int
    signals_today: int
    current_accuracy: float
    mrr: float
    uptime: int
    services_health: List[ServiceHealthResponse]
    recent_events: List[Dict[str, Any]]


class SignalPerformanceResponse(BaseModel):
    signals_today: int
    current_accuracy: float
    avg_confidence: float
    active_circuits: int
    accuracy_trend: List[Dict[str, Any]]


class MT5StatusResponse(BaseModel):
    connected: bool
    account: Optional[str] = None
    broker: Optional[str] = None
    balance: Optional[float] = None
    equity: Optional[float] = None
    last_heartbeat: Optional[str] = None


class UserActivityResponse(BaseModel):
    dau: int  # Daily Active Users
    wau: int  # Weekly Active Users
    mau: int  # Monthly Active Users


class RevenueResponse(BaseModel):
    mrr: float
    arr: float
    revenue_this_period: float
    revenue_trend: List[Dict[str, Any]]
    payment_stats: Dict[str, Any]


class AlertResponse(BaseModel):
    id: str
    severity: str
    type: str
    message: str
    timestamp: str
    status: str


class PerformanceMetricsResponse(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    api_requests_per_sec: int
    metrics_data: List[Dict[str, Any]]


# Dashboard Overview
@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(user: User = Depends(require_plan("admin"))):
    """Get system overview metrics for admin dashboard."""
    try:
        user_queries = UserQueries()
        signal_queries = SignalQueries()
        subscription_queries = SubscriptionQueries()

        # Get user metrics
        all_users = user_queries.get_all_users() or []
        active_users = len([u for u in all_users if u.status == "active"])

        # Get signal metrics
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        signals_today = signal_queries.count_signals_since(today_start) or 0

        # Calculate accuracy (mock for now)
        current_accuracy = 0.96

        # Get MRR
        active_subscriptions = subscription_queries.get_active_subscriptions() or []
        mrr = sum([sub.monthly_fee for sub in active_subscriptions])

        # System uptime (mock)
        uptime = 172800  # 48 hours in seconds

        # Service health checks (mock)
        services_health = [
            ServiceHealthResponse(
                name="FastAPI Backend", status="healthy", response_time=45
            ),
            ServiceHealthResponse(
                name="Quantum Engine", status="healthy", response_time=120
            ),
            ServiceHealthResponse(
                name="MT5 Connector", status="degraded", response_time=350
            ),
            ServiceHealthResponse(
                name="PostgreSQL", status="healthy", response_time=15
            ),
            ServiceHealthResponse(
                name="Redis Cache", status="healthy", response_time=5
            ),
            ServiceHealthResponse(
                name="Celery Workers", status="healthy", response_time=25
            ),
        ]

        # Recent events (mock)
        recent_events = [
            {
                "id": "1",
                "type": "signal_generated",
                "message": "New quantum signal generated for EURUSD",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat(),
            },
            {
                "id": "2",
                "type": "user_registered",
                "message": "New user signed up: john@example.com",
                "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=15)).isoformat(),
            },
            {
                "id": "3",
                "type": "payment_received",
                "message": "Payment processed: R1,000.00",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
            },
        ]

        return DashboardOverviewResponse(
            active_users=active_users,
            signals_today=signals_today,
            current_accuracy=current_accuracy,
            mrr=mrr,
            uptime=uptime,
            services_health=services_health,
            recent_events=recent_events,
        )

    except Exception as e:
        logger.error(f"Dashboard overview error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard overview",
        )


# Signal Performance
@router.get("/signals/performance", response_model=SignalPerformanceResponse)
async def get_signal_performance(
    timeframe: str = "7d", user: User = Depends(require_plan("admin"))
):
    """Get quantum signal performance metrics."""
    try:
        signal_queries = SignalQueries()

        # Get signals for timeframe
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        signals_today = signal_queries.count_signals_since(today_start) or 0

        # Mock metrics
        current_accuracy = 0.96
        avg_confidence = 0.89
        active_circuits = 3

        # Mock accuracy trend
        accuracy_trend = [
            {"time": "00:00", "accuracy": 0.94},
            {"time": "04:00", "accuracy": 0.96},
            {"time": "08:00", "accuracy": 0.95},
            {"time": "12:00", "accuracy": 0.97},
            {"time": "16:00", "accuracy": 0.96},
            {"time": "20:00", "accuracy": 0.98},
        ]

        return SignalPerformanceResponse(
            signals_today=signals_today,
            current_accuracy=current_accuracy,
            avg_confidence=avg_confidence,
            active_circuits=active_circuits,
            accuracy_trend=accuracy_trend,
        )

    except Exception as e:
        logger.error(f"Signal performance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve signal performance",
        )


# MT5 Status
@router.get("/mt5/status", response_model=MT5StatusResponse)
async def get_mt5_status(user: User = Depends(require_plan("admin"))):
    """Get MT5 connection status and account info."""
    try:
        # Mock MT5 status (integrate with actual MT5 connector later)
        return MT5StatusResponse(
            connected=True,
            account="12345678",
            broker="Demo-MT5",
            balance=10000.0,
            equity=10025.0,
            last_heartbeat=(datetime.now(timezone.utc) - timedelta(seconds=30)).isoformat(),
        )

    except Exception as e:
        logger.error(f"MT5 status error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve MT5 status",
        )


# User Management
@router.get("/users")
async def get_users(
    status: Optional[str] = None,
    plan: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    user: User = Depends(require_plan("admin")),
):
    """Get users with filtering."""
    try:
        user_queries = UserQueries()
        users = user_queries.get_all_users() or []

        # Filter by status
        if status:
            users = [u for u in users if u.status == status]

        # Filter by plan
        if plan:
            users = [u for u in users if u.plan == plan]

        # Pagination
        total_count = len(users)
        users = users[offset : offset + limit]

        return {
            "users": users,
            "total_count": total_count,
        }

    except Exception as e:
        logger.error(f"Get users error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users",
        )


# Revenue Metrics
@router.get("/revenue", response_model=RevenueResponse)
async def get_revenue(
    timeframe: str = "month", user: User = Depends(require_plan("admin"))
):
    """Get revenue metrics and financial data."""
    try:
        subscription_queries = SubscriptionQueries()
        active_subscriptions = subscription_queries.get_active_subscriptions() or []

        mrr = sum([sub.monthly_fee for sub in active_subscriptions])
        arr = mrr * 12

        # Mock revenue data
        revenue_this_period = 42500.0

        revenue_trend = [
            {"month": "Jun", "revenue": 12000},
            {"month": "Jul", "revenue": 18000},
            {"month": "Aug", "revenue": 25000},
            {"month": "Sep", "revenue": 32000},
            {"month": "Oct", "revenue": 38000},
            {"month": "Nov", "revenue": 45000},
        ]

        payment_stats = {
            "successful_today": 12,
            "failed_today": 1,
            "pending_today": 2,
            "total_volume": 15000.0,
        }

        return RevenueResponse(
            mrr=mrr,
            arr=arr,
            revenue_this_period=revenue_this_period,
            revenue_trend=revenue_trend,
            payment_stats=payment_stats,
        )

    except Exception as e:
        logger.error(f"Revenue metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve revenue metrics",
        )


# Configuration
@router.get("/config")
async def get_config(user: User = Depends(require_plan("admin"))):
    """Get system configuration."""
    try:
        return {
            "quantum": {
                "default_qubits": settings.quantum_default_qubits if hasattr(settings, "quantum_default_qubits") else 5,
                "backend": "ibmq_qasm_simulator",
                "error_mitigation": True,
                "min_confidence": 0.95,
            },
            "mt5": {
                "server": "Demo-MT5",
                "auto_trading": False,
                "max_position_size": 0.1,
                "risk_per_trade": 1.0,
            },
        }

    except Exception as e:
        logger.error(f"Get config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve configuration",
        )


@router.put("/config")
async def update_config(
    section: str, settings: Dict[str, Any], user: User = Depends(require_plan("admin"))
):
    """Update system configuration."""
    try:
        logger.info(f"Configuration update requested: {section}")
        # TODO: Implement actual configuration update logic
        return {
            "success": True,
            "updated_config": settings,
            "restart_required": True,
        }

    except Exception as e:
        logger.error(f"Update config error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update configuration",
        )


# Alerts
@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    user: User = Depends(require_plan("admin")),
):
    """Get system alerts."""
    try:
        # Mock alerts
        alerts = [
            {
                "id": "1",
                "severity": "high",
                "type": "Signal Accuracy Drop",
                "message": "Signal accuracy has fallen below 95% threshold",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "status": "active",
            },
            {
                "id": "2",
                "severity": "medium",
                "type": "High API Latency",
                "message": "Average API response time exceeds 2 seconds",
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat(),
                "status": "acknowledged",
            },
        ]

        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a["severity"] == severity]

        # Filter by status
        if status:
            alerts = [a for a in alerts if a["status"] == status]

        return {"alerts": alerts, "total_count": len(alerts)}

    except Exception as e:
        logger.error(f"Get alerts error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts",
        )


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user: User = Depends(require_plan("admin"))):
    """Acknowledge an alert."""
    try:
        logger.info(f"Alert {alert_id} acknowledged by {user.email}")
        return {"success": True, "alert_status": "acknowledged"}

    except Exception as e:
        logger.error(f"Acknowledge alert error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to acknowledge alert",
        )


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, user: User = Depends(require_plan("admin"))):
    """Resolve an alert."""
    try:
        logger.info(f"Alert {alert_id} resolved by {user.email}")
        return {"success": True, "alert_status": "resolved"}

    except Exception as e:
        logger.error(f"Resolve alert error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resolve alert",
        )


# Performance Metrics
@router.get("/performance", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    metric_type: Optional[str] = None,
    timeframe: str = "1h",
    user: User = Depends(require_plan("admin")),
):
    """Get system performance metrics."""
    try:
        # Mock performance data
        metrics_data = [
            {"time": "10:00", "usage": 35},
            {"time": "10:15", "usage": 42},
            {"time": "10:30", "usage": 45},
            {"time": "10:45", "usage": 48},
            {"time": "11:00", "usage": 45},
        ]

        return PerformanceMetricsResponse(
            cpu_usage=45.0,
            memory_usage=68.0,
            disk_usage=42.0,
            api_requests_per_sec=125,
            metrics_data=metrics_data,
        )

    except Exception as e:
        logger.error(f"Performance metrics error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance metrics",
        )
