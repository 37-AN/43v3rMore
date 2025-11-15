"""Subscription management service."""

from typing import Optional
from datetime import datetime, timezone, timedelta
from uuid import UUID
from loguru import logger

from ..database.queries import SubscriptionQueries, UserQueries
from ..database.models import Subscription, User


class SubscriptionManager:
    """Manage user subscriptions."""

    def __init__(self):
        """Initialize subscription manager."""
        self.sub_queries = SubscriptionQueries()
        self.user_queries = UserQueries()
        logger.info("Subscription manager initialized")

    def create_subscription(
        self,
        user_id: UUID,
        plan: str,
        monthly_fee: float,
    ) -> Optional[Subscription]:
        """Create new subscription."""
        try:
            sub_data = {
                "user_id": str(user_id),
                "plan": plan,
                "monthly_fee": monthly_fee,
                "currency": "ZAR",
                "status": "active",
                "current_period_start": datetime.now(timezone.utc).isoformat(),
                "current_period_end": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "next_billing_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
            }

            subscription = self.sub_queries.create_subscription(sub_data)

            if subscription:
                # Update user plan
                self.user_queries.update_user(user_id, {"plan": plan})

            return subscription

        except Exception as e:
            logger.error(f"Create subscription error: {e}")
            return None

    def cancel_subscription(self, subscription_id: UUID) -> bool:
        """Cancel subscription."""
        try:
            updated = self.sub_queries.update_subscription(
                subscription_id,
                {"status": "cancelled", "cancel_at_period_end": True},
            )

            return updated is not None

        except Exception as e:
            logger.error(f"Cancel subscription error: {e}")
            return False

    def upgrade_subscription(
        self,
        user_id: UUID,
        new_plan: str,
        new_fee: float,
    ) -> Optional[Subscription]:
        """Upgrade user subscription."""
        try:
            current_sub = self.sub_queries.get_user_subscription(user_id)
            if not current_sub:
                return None

            # Update subscription
            updated = self.sub_queries.update_subscription(
                current_sub.id,
                {"plan": new_plan, "monthly_fee": new_fee},
            )

            if updated:
                # Update user plan
                self.user_queries.update_user(user_id, {"plan": new_plan})

            return updated

        except Exception as e:
            logger.error(f"Upgrade subscription error: {e}")
            return None
