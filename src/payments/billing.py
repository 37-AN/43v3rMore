"""Billing automation service."""

from typing import List
from datetime import datetime, timedelta
from uuid import UUID
from loguru import logger

from ..database.queries import SubscriptionQueries, UserQueries
from ..database.models import Subscription, Payment
from .payfast import PayFastClient


class BillingService:
    """Automated billing service."""

    def __init__(self):
        """Initialize billing service."""
        self.sub_queries = SubscriptionQueries()
        self.user_queries = UserQueries()
        self.payfast = PayFastClient()
        logger.info("Billing service initialized")

    def process_due_subscriptions(self) -> int:
        """
        Process all subscriptions due for billing.

        Returns:
            Number of subscriptions processed

        Example:
            >>> billing = BillingService()
            >>> count = billing.process_due_subscriptions()
        """
        try:
            due_subs = self.sub_queries.get_due_subscriptions()
            processed = 0

            for sub in due_subs:
                if self.process_subscription_renewal(sub):
                    processed += 1

            logger.info(
                f"Processed {processed}/{len(due_subs)} subscriptions",
                extra={"processed": processed, "total": len(due_subs)},
            )

            return processed

        except Exception as e:
            logger.error(f"Billing processing error: {e}")
            return 0

    def process_subscription_renewal(self, subscription: Subscription) -> bool:
        """Process individual subscription renewal."""
        try:
            # Get user
            user = self.user_queries.get_user_by_id(subscription.user_id)
            if not user:
                logger.error(f"User not found for subscription: {subscription.id}")
                return False

            # Generate payment URL
            payment_url = self.payfast.create_subscription_payment(
                user_id=str(user.id),
                plan=subscription.plan,
                amount=float(subscription.monthly_fee),
                email=user.email,
                name=user.name or "",
            )

            # Send payment link via email/notification
            # This would integrate with communication channels

            # Update next billing date
            next_billing = subscription.next_billing_date + timedelta(days=30)
            self.sub_queries.update_subscription(
                subscription.id,
                {"next_billing_date": next_billing.isoformat()},
            )

            logger.info(
                f"Subscription renewal processed: {user.email}",
                extra={"user_id": str(user.id), "plan": subscription.plan},
            )

            return True

        except Exception as e:
            logger.error(f"Subscription renewal error: {e}")
            return False
