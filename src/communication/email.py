"""Email service for signal delivery."""

from typing import List, Dict, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from loguru import logger

from ..utils.config import get_settings

settings = get_settings()


class EmailService:
    """Email service using SendGrid."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize email service.

        Args:
            api_key: SendGrid API key

        Example:
            >>> email_service = EmailService()
            >>> email_service.send_signal("user@example.com", signal_data)
        """
        self.api_key = api_key or settings.sendgrid_api_key
        self.from_email = settings.sendgrid_from_email

        if not self.api_key:
            logger.warning("SendGrid API key not configured")
            self.client = None
            return

        try:
            self.client = SendGridAPIClient(self.api_key)
            logger.info("Email service initialized")
        except Exception as e:
            logger.error(f"Email service initialization error: {e}")
            self.client = None

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        Send email.

        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body

        Returns:
            True if sent successfully
        """
        if not self.client:
            logger.warning("Email client not configured")
            return False

        try:
            message = Mail(
                from_email=Email(self.from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
            )

            if text_content:
                message.plain_text_content = Content("text/plain", text_content)

            response = self.client.send(message)

            logger.info(
                f"Email sent to {to_email}: {subject}",
                extra={"to": to_email, "status": response.status_code},
            )

            return response.status_code in [200, 201, 202]

        except Exception as e:
            logger.error(f"Email send error to {to_email}: {e}")
            return False

    def send_signal(self, to_email: str, signal: Dict) -> bool:
        """
        Send trading signal via email.

        Args:
            to_email: Recipient email
            signal: Signal data

        Returns:
            True if sent successfully
        """
        subject = f"Trading Signal: {signal.get('action')} {signal.get('symbol')}"

        html_content = self._format_signal_html(signal)
        text_content = self._format_signal_text(signal)

        return self.send_email(to_email, subject, html_content, text_content)

    def _format_signal_html(self, signal: Dict) -> str:
        """Format signal as HTML email."""
        confidence_pct = signal.get("confidence", 0) * 100

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .signal {{ background: #f5f5f5; padding: 20px; border-radius: 10px; }}
                .action-buy {{ color: #00c853; font-weight: bold; }}
                .action-sell {{ color: #d50000; font-weight: bold; }}
                .detail {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="signal">
                <h2>🔔 Trading Signal</h2>

                <div class="detail">
                    <span class="label">Symbol:</span> {signal.get('symbol')}
                </div>

                <div class="detail">
                    <span class="label">Action:</span>
                    <span class="action-{signal.get('action', '').lower()}">{signal.get('action')}</span>
                </div>

                <div class="detail">
                    <span class="label">Entry Price:</span> {signal.get('entry_price'):.5f}
                </div>

                <div class="detail">
                    <span class="label">Stop Loss:</span> {signal.get('stop_loss'):.5f}
                </div>

                <div class="detail">
                    <span class="label">Take Profit:</span> {signal.get('take_profit'):.5f}
                </div>

                <div class="detail">
                    <span class="label">Confidence:</span> {confidence_pct:.1f}%
                </div>

                <div class="detail">
                    <span class="label">Reason:</span> {signal.get('reason', 'Quantum analysis')}
                </div>

                <hr>

                <h3>⚠️ Risk Management</h3>
                <ul>
                    <li>Use proper position sizing</li>
                    <li>Never risk more than 2% per trade</li>
                    <li>Set stop loss immediately</li>
                </ul>

                <p><em>Good luck! 🚀</em></p>
            </div>
        </body>
        </html>
        """

        return html

    def _format_signal_text(self, signal: Dict) -> str:
        """Format signal as plain text email."""
        confidence_pct = signal.get("confidence", 0) * 100

        text = f"""
TRADING SIGNAL

Symbol: {signal.get('symbol')}
Action: {signal.get('action')}
Entry: {signal.get('entry_price'):.5f}
Stop Loss: {signal.get('stop_loss'):.5f}
Take Profit: {signal.get('take_profit'):.5f}
Confidence: {confidence_pct:.1f}%

Reason: {signal.get('reason', 'Quantum analysis')}

RISK MANAGEMENT:
- Use proper position sizing
- Never risk more than 2% per trade
- Set stop loss immediately

Good luck!
        """

        return text.strip()

    def send_welcome_email(self, to_email: str, name: str) -> bool:
        """Send welcome email to new user."""
        subject = "Welcome to Quantum Trading AI!"

        html_content = f"""
        <html>
        <body>
            <h1>Welcome {name}!</h1>
            <p>Thank you for joining Quantum Trading AI.</p>
            <p>You'll start receiving high-accuracy trading signals soon.</p>
            <h3>Next Steps:</h3>
            <ul>
                <li>Configure your Telegram for instant signals</li>
                <li>Review our trading guide</li>
                <li>Set up your trading platform</li>
            </ul>
            <p>Best regards,<br>The Quantum Trading AI Team</p>
        </body>
        </html>
        """

        return self.send_email(to_email, subject, html_content)
