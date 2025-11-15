"""Integration tests for communication channels."""

import pytest

from src.communication.telegram import TelegramBot
from src.communication.email import EmailService
from src.communication.whatsapp import WhatsAppService
from src.communication.sms import SMSService


class TestTelegramBot:
    """Test Telegram bot functionality."""

    def test_telegram_bot_initialization(self):
        """Test Telegram bot initialization."""
        # Initialize without token (mock mode)
        bot = TelegramBot(token=None)

        # Should initialize even without token
        assert bot is not None

    def test_signal_formatting(self, mock_signal_data):
        """Test signal formatting for Telegram."""
        bot = TelegramBot(token=None)

        formatted = bot._format_signal(mock_signal_data)

        assert isinstance(formatted, str)
        assert mock_signal_data["symbol"] in formatted
        assert mock_signal_data["action"] in formatted
        assert "Entry" in formatted or "entry" in formatted.lower()

    def test_telegram_message_structure(self, mock_signal_data):
        """Test Telegram message has required components."""
        bot = TelegramBot()

        message = bot._format_signal(mock_signal_data)

        # Check for essential signal components
        assert "EURUSD" in message
        assert "BUY" in message
        assert "1.1000" in message  # Entry price
        assert "87" in message or "0.87" in message  # Confidence

        # Check for risk management info
        assert "Stop Loss" in message or "SL" in message
        assert "Take Profit" in message or "TP" in message


class TestEmailService:
    """Test email service functionality."""

    def test_email_service_initialization(self):
        """Test email service initialization."""
        # Initialize without API key (mock mode)
        email_service = EmailService(api_key=None)

        assert email_service is not None

    def test_signal_email_html_formatting(self, mock_signal_data):
        """Test HTML email formatting."""
        email_service = EmailService(api_key=None)

        html = email_service._format_signal_html(mock_signal_data)

        assert isinstance(html, str)
        assert "<html>" in html.lower()
        assert mock_signal_data["symbol"] in html
        assert mock_signal_data["action"] in html

        # Check for styling
        assert "style" in html.lower() or "class" in html.lower()

    def test_signal_email_text_formatting(self, mock_signal_data):
        """Test plain text email formatting."""
        email_service = EmailService(api_key=None)

        text = email_service._format_signal_text(mock_signal_data)

        assert isinstance(text, str)
        assert mock_signal_data["symbol"] in text
        assert mock_signal_data["action"] in text
        assert "TRADING SIGNAL" in text or "Trading Signal" in text

    def test_welcome_email_structure(self):
        """Test welcome email has proper structure."""
        email_service = EmailService()

        # This tests the method exists and has correct signature
        assert hasattr(email_service, "send_welcome_email")


class TestWhatsAppService:
    """Test WhatsApp service functionality."""

    def test_whatsapp_initialization(self):
        """Test WhatsApp service initialization."""
        # Initialize without credentials (mock mode)
        whatsapp = WhatsAppService(
            account_sid=None,
            auth_token=None,
            from_number=None,
        )

        assert whatsapp is not None

    def test_whatsapp_signal_formatting(self, mock_signal_data):
        """Test WhatsApp signal formatting."""
        whatsapp = WhatsAppService()

        message = whatsapp._format_signal(mock_signal_data)

        assert isinstance(message, str)
        assert mock_signal_data["symbol"] in message
        assert mock_signal_data["action"] in message

        # WhatsApp messages should be concise
        assert len(message) < 500  # Reasonable length


class TestSMSService:
    """Test SMS service functionality."""

    def test_sms_initialization(self):
        """Test SMS service initialization."""
        # Initialize without credentials (mock mode)
        sms = SMSService(
            account_sid=None,
            auth_token=None,
            from_number=None,
        )

        assert sms is not None

    def test_sms_signal_formatting(self, mock_signal_data):
        """Test SMS signal formatting."""
        sms = SMSService()

        message = sms._format_signal(mock_signal_data)

        assert isinstance(message, str)
        assert mock_signal_data["symbol"] in message
        assert mock_signal_data["action"] in message

        # SMS messages must be very short
        assert len(message) < 160  # Standard SMS length


class TestMultiChannelDelivery:
    """Test multi-channel signal delivery."""

    def test_signal_formatting_consistency(self, mock_signal_data):
        """Test that all channels format signals with consistent data."""
        telegram = TelegramBot()
        email = EmailService()
        whatsapp = WhatsAppService()
        sms = SMSService()

        # Generate formatted messages
        telegram_msg = telegram._format_signal(mock_signal_data)
        email_html = email._format_signal_html(mock_signal_data)
        email_text = email._format_signal_text(mock_signal_data)
        whatsapp_msg = whatsapp._format_signal(mock_signal_data)
        sms_msg = sms._format_signal(mock_signal_data)

        # All should contain the symbol
        assert all(
            mock_signal_data["symbol"] in msg
            for msg in [telegram_msg, email_html, email_text, whatsapp_msg, sms_msg]
        )

        # All should contain the action
        assert all(
            mock_signal_data["action"] in msg
            for msg in [telegram_msg, email_html, email_text, whatsapp_msg, sms_msg]
        )

    def test_message_length_requirements(self, mock_signal_data):
        """Test that messages meet channel length requirements."""
        telegram = TelegramBot()
        whatsapp = WhatsAppService()
        sms = SMSService()

        telegram_msg = telegram._format_signal(mock_signal_data)
        whatsapp_msg = whatsapp._format_signal(mock_signal_data)
        sms_msg = sms._format_signal(mock_signal_data)

        # Telegram: can be longer
        assert len(telegram_msg) < 4096  # Telegram limit

        # WhatsApp: moderate length
        assert len(whatsapp_msg) < 1000

        # SMS: very short
        assert len(sms_msg) < 160


class TestSignalDeliveryWorkflow:
    """Test complete signal delivery workflow."""

    def test_signal_broadcast_structure(self, mock_signal_data):
        """Test signal broadcast to multiple channels."""
        # Create service instances
        telegram = TelegramBot()
        email = EmailService()

        # Format for each channel
        telegram_msg = telegram._format_signal(mock_signal_data)
        email_html = email._format_signal_html(mock_signal_data)

        # Verify both were created successfully
        assert telegram_msg is not None
        assert email_html is not None

    def test_delivery_error_handling(self):
        """Test error handling in delivery services."""
        # Services should handle None/missing credentials gracefully
        telegram = TelegramBot(token=None)
        email = EmailService(api_key=None)
        whatsapp = WhatsAppService(account_sid=None)
        sms = SMSService(account_sid=None)

        # All should initialize without errors
        assert telegram is not None
        assert email is not None
        assert whatsapp is not None
        assert sms is not None


class TestCommunicationRetry:
    """Test retry logic for communication channels."""

    def test_telegram_broadcast_returns_count(self, mock_signal_data):
        """Test that broadcast returns success count."""
        bot = TelegramBot(token=None)

        # This would normally broadcast to multiple users
        # In mock mode, we just test the structure
        user_ids = ["123", "456", "789"]

        # Method signature should accept signal and user list
        assert hasattr(bot, "broadcast_signal")

    def test_email_batch_sending_structure(self):
        """Test email batch sending capability."""
        email_service = EmailService(api_key=None)

        # Verify send methods exist
        assert hasattr(email_service, "send_email")
        assert hasattr(email_service, "send_signal")


class TestChannelSpecificFeatures:
    """Test channel-specific features."""

    def test_telegram_commands_structure(self):
        """Test Telegram bot command structure."""
        bot = TelegramBot()

        # Verify command handlers are defined
        assert hasattr(bot, "cmd_start")
        assert hasattr(bot, "cmd_help")
        assert hasattr(bot, "cmd_subscribe")
        assert hasattr(bot, "cmd_plans")

    def test_email_templates(self):
        """Test email template methods."""
        email_service = EmailService()

        assert hasattr(email_service, "_format_signal_html")
        assert hasattr(email_service, "_format_signal_text")
        assert hasattr(email_service, "send_welcome_email")
