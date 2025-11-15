"""SMS service using Twilio."""

from typing import Dict, Optional
from twilio.rest import Client
from loguru import logger

from ..utils.config import get_settings

settings = get_settings()


class SMSService:
    """SMS messaging service via Twilio."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
    ):
        """Initialize SMS service."""
        self.account_sid = account_sid or settings.twilio_account_sid
        self.auth_token = auth_token or settings.twilio_auth_token
        self.from_number = from_number or settings.twilio_phone_from

        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio SMS not configured")
            self.client = None
            return

        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("SMS service initialized")
        except Exception as e:
            logger.error(f"SMS service error: {e}")
            self.client = None

    def send_sms(self, to_number: str, message: str) -> bool:
        """Send SMS message."""
        if not self.client:
            logger.warning("SMS client not configured")
            return False

        try:
            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number,
            )

            logger.info(f"SMS sent to {to_number}: {msg.sid}")
            return True

        except Exception as e:
            logger.error(f"SMS send error: {e}")
            return False

    def send_signal(self, to_number: str, signal: Dict) -> bool:
        """Send trading signal via SMS (shortened format)."""
        message = self._format_signal(signal)
        return self.send_sms(to_number, message)

    def _format_signal(self, signal: Dict) -> str:
        """Format signal for SMS (keep it short)."""
        confidence_pct = signal.get("confidence", 0) * 100

        return (
            f"SIGNAL: {signal.get('action')} {signal.get('symbol')} @ "
            f"{signal.get('entry_price'):.5f} | SL:{signal.get('stop_loss'):.5f} | "
            f"TP:{signal.get('take_profit'):.5f} | {confidence_pct:.0f}%"
        )
