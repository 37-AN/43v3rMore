"""PayFast payment integration for South Africa."""

from typing import Dict, Optional
import hashlib
import urllib.parse
from loguru import logger

from ..utils.config import get_settings

settings = get_settings()


class PayFastClient:
    """PayFast payment gateway client."""

    def __init__(
        self,
        merchant_id: Optional[str] = None,
        merchant_key: Optional[str] = None,
        passphrase: Optional[str] = None,
        sandbox: bool = True,
    ):
        """
        Initialize PayFast client.

        Args:
            merchant_id: PayFast merchant ID
            merchant_key: PayFast merchant key
            passphrase: PayFast passphrase
            sandbox: Use sandbox environment

        Example:
            >>> payfast = PayFastClient()
            >>> payment_url = payfast.generate_payment_url(amount=500, item_name="Pro Plan")
        """
        self.merchant_id = merchant_id or settings.payfast_merchant_id
        self.merchant_key = merchant_key or settings.payfast_merchant_key
        self.passphrase = passphrase or settings.payfast_passphrase
        self.sandbox = sandbox or settings.payfast_sandbox

        self.base_url = (
            "https://sandbox.payfast.co.za/eng/process"
            if self.sandbox
            else "https://www.payfast.co.za/eng/process"
        )

        logger.info(
            f"PayFast initialized: {'sandbox' if self.sandbox else 'production'}",
            extra={"sandbox": self.sandbox},
        )

    def generate_signature(self, data: Dict) -> str:
        """
        Generate MD5 signature for PayFast.

        Args:
            data: Payment data dictionary

        Returns:
            MD5 signature string
        """
        # Create parameter string
        param_string = "&".join(f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in sorted(data.items()))

        # Add passphrase if configured
        if self.passphrase:
            param_string += f"&passphrase={urllib.parse.quote_plus(self.passphrase)}"

        # Generate signature
        signature = hashlib.md5(param_string.encode()).hexdigest()

        logger.debug(f"Generated signature: {signature}")
        return signature

    def generate_payment_url(
        self,
        amount: float,
        item_name: str,
        item_description: str = "",
        email_address: str = "",
        name_first: str = "",
        name_last: str = "",
        return_url: str = "",
        cancel_url: str = "",
        notify_url: str = "",
    ) -> str:
        """
        Generate PayFast payment URL.

        Args:
            amount: Payment amount
            item_name: Item description
            item_description: Detailed description
            email_address: Customer email
            name_first: Customer first name
            name_last: Customer last name
            return_url: URL to redirect after successful payment
            cancel_url: URL to redirect if cancelled
            notify_url: ITN (Instant Transaction Notification) URL

        Returns:
            Complete payment URL

        Example:
            >>> url = payfast.generate_payment_url(
            ...     amount=1000,
            ...     item_name="Pro Plan Subscription",
            ...     email_address="user@example.com"
            ... )
        """
        data = {
            "merchant_id": self.merchant_id,
            "merchant_key": self.merchant_key,
            "amount": f"{amount:.2f}",
            "item_name": item_name,
        }

        # Optional fields
        if item_description:
            data["item_description"] = item_description
        if email_address:
            data["email_address"] = email_address
        if name_first:
            data["name_first"] = name_first
        if name_last:
            data["name_last"] = name_last
        if return_url:
            data["return_url"] = return_url
        if cancel_url:
            data["cancel_url"] = cancel_url
        if notify_url:
            data["notify_url"] = notify_url

        # Generate signature
        data["signature"] = self.generate_signature(data)

        # Build URL
        query_string = urllib.parse.urlencode(data)
        payment_url = f"{self.base_url}?{query_string}"

        logger.info(
            f"Payment URL generated: {item_name} - R{amount}",
            extra={"amount": amount, "item": item_name},
        )

        return payment_url

    def verify_payment(self, post_data: Dict) -> bool:
        """
        Verify PayFast ITN (Instant Transaction Notification).

        Args:
            post_data: POST data from PayFast ITN

        Returns:
            True if payment is valid

        Example:
            >>> if payfast.verify_payment(request.POST):
            ...     # Payment verified
            ...     activate_subscription(user_id)
        """
        try:
            # Extract signature
            signature = post_data.get("signature", "")
            data = {k: v for k, v in post_data.items() if k != "signature"}

            # Generate expected signature
            expected_signature = self.generate_signature(data)

            # Verify
            is_valid = signature == expected_signature

            if is_valid:
                logger.info(
                    "Payment verified",
                    extra={"payment_id": post_data.get("m_payment_id")},
                )
            else:
                logger.warning(
                    "Payment verification failed",
                    extra={"payment_id": post_data.get("m_payment_id")},
                )

            return is_valid

        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return False

    def create_subscription_payment(
        self,
        user_id: str,
        plan: str,
        amount: float,
        email: str,
        name: str = "",
    ) -> str:
        """
        Create subscription payment URL.

        Args:
            user_id: User ID
            plan: Subscription plan
            amount: Monthly amount
            email: User email
            name: User name

        Returns:
            Payment URL
        """
        return self.generate_payment_url(
            amount=amount,
            item_name=f"{plan.capitalize()} Plan Subscription",
            item_description=f"Monthly subscription to {plan} plan",
            email_address=email,
            name_first=name.split()[0] if name else "",
            name_last=" ".join(name.split()[1:]) if len(name.split()) > 1 else "",
        )
