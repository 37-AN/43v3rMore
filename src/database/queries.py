"""Database query abstractions."""

from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime, timezone, timezone, timedelta
from loguru import logger

from .supabase import get_supabase_client
from .models import User, Subscription, Signal, AnalyticsEvent


class UserQueries:
    """User database queries."""

    def __init__(self):
        """Initialize user queries."""
        self.db = get_supabase_client()

    def create_user(self, user_data: Dict) -> Optional[User]:
        """
        Create new user.

        Args:
            user_data: User data dictionary

        Returns:
            Created User or None

        Example:
            >>> queries = UserQueries()
            >>> user = queries.create_user({"email": "test@example.com", "plan": "basic"})
        """
        try:
            result = self.db.insert("users", user_data)
            if result:
                logger.info(f"User created: {user_data.get('email')}")
                return User(**result)
            return None
        except Exception as e:
            logger.error(f"User creation error: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            users = self.db.select("users", filters={"email": email}, limit=1)
            return User(**users[0]) if users else None
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None

    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        try:
            users = self.db.select("users", filters={"id": str(user_id)}, limit=1)
            return User(**users[0]) if users else None
        except Exception as e:
            logger.error(f"Get user error: {e}")
            return None

    def update_user(self, user_id: UUID, updates: Dict) -> Optional[User]:
        """Update user."""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            result = self.db.update("users", updates, {"id": str(user_id)})
            if result:
                logger.info(f"User updated: {user_id}")
                return User(**result)
            return None
        except Exception as e:
            logger.error(f"User update error: {e}")
            return None

    def get_active_users(self, plan: Optional[str] = None) -> List[User]:
        """Get all active users, optionally filtered by plan."""
        try:
            filters = {"status": "active"}
            if plan:
                filters["plan"] = plan

            users = self.db.select("users", filters=filters)
            return [User(**u) for u in users]
        except Exception as e:
            logger.error(f"Get active users error: {e}")
            return []


class SubscriptionQueries:
    """Subscription database queries."""

    def __init__(self):
        """Initialize subscription queries."""
        self.db = get_supabase_client()

    def create_subscription(self, sub_data: Dict) -> Optional[Subscription]:
        """Create new subscription."""
        try:
            result = self.db.insert("subscriptions", sub_data)
            if result:
                logger.info(f"Subscription created for user: {sub_data.get('user_id')}")
                return Subscription(**result)
            return None
        except Exception as e:
            logger.error(f"Subscription creation error: {e}")
            return None

    def get_user_subscription(self, user_id: UUID) -> Optional[Subscription]:
        """Get active subscription for user."""
        try:
            subs = self.db.select(
                "subscriptions",
                filters={"user_id": str(user_id), "status": "active"},
                limit=1,
            )
            return Subscription(**subs[0]) if subs else None
        except Exception as e:
            logger.error(f"Get subscription error: {e}")
            return None

    def update_subscription(
        self, subscription_id: UUID, updates: Dict
    ) -> Optional[Subscription]:
        """Update subscription."""
        try:
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            result = self.db.update(
                "subscriptions", updates, {"id": str(subscription_id)}
            )
            if result:
                logger.info(f"Subscription updated: {subscription_id}")
                return Subscription(**result)
            return None
        except Exception as e:
            logger.error(f"Subscription update error: {e}")
            return None

    def get_due_subscriptions(self) -> List[Subscription]:
        """Get subscriptions due for billing."""
        try:
            today = datetime.now(timezone.utc).date().isoformat()
            subs = self.db.select(
                "subscriptions",
                filters={"status": "active"},
            )

            # Filter by next_billing_date
            due_subs = [
                Subscription(**s)
                for s in subs
                if s.get("next_billing_date", "") <= today
            ]

            return due_subs
        except Exception as e:
            logger.error(f"Get due subscriptions error: {e}")
            return []


class SignalQueries:
    """Signal database queries."""

    def __init__(self):
        """Initialize signal queries."""
        self.db = get_supabase_client()

    def create_signal(self, signal_data: Dict) -> Optional[Signal]:
        """Create new signal."""
        try:
            result = self.db.insert("signals", signal_data)
            if result:
                logger.info(f"Signal created: {signal_data.get('symbol')}")
                return Signal(**result)
            return None
        except Exception as e:
            logger.error(f"Signal creation error: {e}")
            return None

    def get_recent_signals(
        self, symbol: Optional[str] = None, limit: int = 10
    ) -> List[Signal]:
        """Get recent signals."""
        try:
            filters = {}
            if symbol:
                filters["symbol"] = symbol

            signals = self.db.select("signals", filters=filters, limit=limit)
            return [Signal(**s) for s in signals]
        except Exception as e:
            logger.error(f"Get recent signals error: {e}")
            return []

    def get_signal_by_id(self, signal_id: UUID) -> Optional[Signal]:
        """Get signal by ID."""
        try:
            signals = self.db.select("signals", filters={"id": str(signal_id)}, limit=1)
            return Signal(**signals[0]) if signals else None
        except Exception as e:
            logger.error(f"Get signal error: {e}")
            return None

    def update_signal_status(
        self, signal_id: UUID, status: str, result_pnl: Optional[float] = None
    ) -> Optional[Signal]:
        """Update signal status."""
        try:
            updates = {"status": status}
            if result_pnl is not None:
                updates["result_pnl"] = result_pnl

            result = self.db.update("signals", updates, {"id": str(signal_id)})
            if result:
                logger.info(f"Signal status updated: {signal_id} -> {status}")
                return Signal(**result)
            return None
        except Exception as e:
            logger.error(f"Signal update error: {e}")
            return None

    def get_signal_performance(self, days: int = 30) -> Dict:
        """Get signal performance statistics."""
        try:
            since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

            # This would use a Supabase function for complex queries
            # For now, return basic structure
            return {
                "period_days": days,
                "total_signals": 0,
                "winning_signals": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
            }
        except Exception as e:
            logger.error(f"Performance calculation error: {e}")
            return {}


class AnalyticsQueries:
    """Analytics database queries."""

    def __init__(self):
        """Initialize analytics queries."""
        self.db = get_supabase_client()

    def track_event(self, event_type: str, user_id: Optional[UUID], data: Dict) -> bool:
        """Track analytics event."""
        try:
            event = {
                "event_type": event_type,
                "user_id": str(user_id) if user_id else None,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            result = self.db.insert("analytics_events", event)
            return result is not None
        except Exception as e:
            logger.error(f"Event tracking error: {e}")
            return False

    def get_events(
        self, event_type: Optional[str] = None, limit: int = 100
    ) -> List[AnalyticsEvent]:
        """Get analytics events."""
        try:
            filters = {}
            if event_type:
                filters["event_type"] = event_type

            events = self.db.select("analytics_events", filters=filters, limit=limit)
            return [AnalyticsEvent(**e) for e in events]
        except Exception as e:
            logger.error(f"Get events error: {e}")
            return []

    def get_dashboard_metrics(self) -> Dict:
        """Get dashboard metrics."""
        try:
            # This would use Supabase functions for aggregations
            return {
                "total_users": 0,
                "active_subscriptions": 0,
                "signals_today": 0,
                "revenue_this_month": 0.0,
            }
        except Exception as e:
            logger.error(f"Metrics calculation error: {e}")
            return {}
