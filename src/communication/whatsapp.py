"""WhatsApp service using Twilio."""

from typing import Dict, Optional
from twilio.rest import Client
from loguru import logger

from ..utils.config import get_settings

settings = get_settings()


class WhatsAppService:
    """WhatsApp messaging service via Twilio."""

    def __init__(
        self,
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_number: Optional[str] = None,
    ):
        """Initialize WhatsApp service."""
        self.account_sid = account_sid or settings.twilio_account_sid
        self.auth_token = auth_token or settings.twilio_auth_token
        self.from_number = from_number or settings.twilio_whatsapp_from

        if not all([self.account_sid, self.auth_token, self.from_number]):
            logger.warning("Twilio WhatsApp not configured")
            self.client = None
            return

        try:
            self.client = Client(self.account_sid, self.auth_token)
            logger.info("WhatsApp service initialized")
        except Exception as e:
            logger.error(f"WhatsApp service error: {e}")
            self.client = None

    def send_message(self, to_number: str, message: str) -> bool:
        """Send WhatsApp message."""
        if not self.client:
            logger.warning("WhatsApp client not configured")
            return False

        try:
            # Ensure number has whatsapp: prefix
            if not to_number.startswith("whatsapp:"):
                to_number = f"whatsapp:{to_number}"

            msg = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number,
            )

            logger.info(f"WhatsApp sent to {to_number}: {msg.sid}")
            return True

        except Exception as e:
            logger.error(f"WhatsApp send error: {e}")
            return False

    def send_signal(self, to_number: str, signal: Dict) -> bool:
        """Send trading signal via WhatsApp."""
        message = self._format_signal(signal)
        return self.send_message(to_number, message)

    def _format_signal(self, signal: Dict) -> str:
        """Format signal for WhatsApp."""
        confidence_pct = signal.get("confidence", 0) * 100

        return f"""
🔔 TRADING SIGNAL

Symbol: {signal.get('symbol')}
Action: {signal.get('action')}
Entry: {signal.get('entry_price'):.5f}
SL: {signal.get('stop_loss'):.5f}
TP: {signal.get('take_profit'):.5f}
Confidence: {confidence_pct:.1f}%

Reason: {signal.get('reason', 'Quantum analysis')}

⚠️ Use proper risk management!
        """.strip()
