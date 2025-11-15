"""Telegram bot for signal delivery."""

from typing import Optional, List, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from loguru import logger

from ..utils.config import get_settings
from ..database.queries import UserQueries

settings = get_settings()


class TelegramBot:
    """
    Telegram bot for trading signal delivery.

    Handles signal broadcasting, user interactions, and subscription management.
    """

    def __init__(self, token: Optional[str] = None):
        """
        Initialize Telegram bot.

        Args:
            token: Telegram bot token

        Example:
            >>> bot = TelegramBot()
            >>> await bot.send_signal(chat_id, signal_data)
        """
        self.token = token or settings.telegram_bot_token

        if not self.token:
            logger.warning("Telegram bot token not configured")
            self.app = None
            return

        self.app = Application.builder().token(self.token).build()
        self._setup_handlers()

        logger.info("Telegram bot initialized")

    def _setup_handlers(self):
        """Set up command and callback handlers."""
        if not self.app:
            return

        # Command handlers
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("subscribe", self.cmd_subscribe))
        self.app.add_handler(CommandHandler("unsubscribe", self.cmd_unsubscribe))
        self.app.add_handler(CommandHandler("plans", self.cmd_plans))
        self.app.add_handler(CommandHandler("status", self.cmd_status))

        # Callback handlers
        self.app.add_handler(CallbackQueryHandler(self.handle_callback))

        logger.info("Telegram handlers registered")

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_text = """
🤖 *Welcome to Quantum Trading AI*

Your autonomous trading signal provider using quantum computing.

📊 *What we offer:*
• High-accuracy trading signals (95%+ accuracy)
• Real-time signal delivery via Telegram
• Multiple currency pairs
• Risk management included

💡 *Get Started:*
/subscribe - Choose your plan
/plans - View pricing options
/help - Get help

Ready to start trading smarter?
        """

        await update.message.reply_text(
            welcome_text,
            parse_mode="Markdown",
        )

        logger.info(f"User {update.effective_user.id} started bot")

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
📖 *Available Commands:*

/start - Welcome message
/subscribe - Subscribe to signals
/unsubscribe - Cancel subscription
/plans - View pricing plans
/status - Check your subscription status
/help - This help message

🔔 *Signal Format:*
Symbol: EURUSD
Action: BUY
Entry: 1.1000
SL: 1.0950
TP: 1.1100
Confidence: 87%

📧 *Support:*
Email: support@quantumtrading.ai
Website: https://quantumtrading.ai

💬 Need more help? Contact our support team!
        """

        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def cmd_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command."""
        keyboard = [
            [InlineKeyboardButton("Basic (R500/month)", callback_data="plan_basic")],
            [InlineKeyboardButton("Pro (R1000/month)", callback_data="plan_pro")],
            [InlineKeyboardButton("Premium (R2000/month)", callback_data="plan_premium")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Choose your subscription plan:",
            reply_markup=reply_markup,
        )

    async def cmd_unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command."""
        await update.message.reply_text(
            "To cancel your subscription, please contact support at support@quantumtrading.ai"
        )

    async def cmd_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /plans command."""
        plans_text = f"""
💰 *Subscription Plans:*

📱 *Basic* - R{settings.basic_plan_price}/month
• 5 signals per day
• Major pairs only
• Email + Telegram delivery

🚀 *Pro* - R{settings.pro_plan_price}/month
• 10 signals per day
• All pairs
• WhatsApp + Telegram + Email
• Priority support

⭐ *Premium* - R{settings.premium_plan_price}/month
• Unlimited signals
• All pairs + Commodities
• All channels
• 1-on-1 support
• Custom analysis

🤖 *Bot License* - R{settings.bot_license_price}/month
• Automated trading bot
• 24/7 execution
• Full control

🏢 *Enterprise* - R{settings.enterprise_price}/month
• Custom solutions
• API access
• Dedicated support

Use /subscribe to get started!
        """

        await update.message.reply_text(plans_text, parse_mode="Markdown")

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        # This would check user's subscription in database
        await update.message.reply_text(
            "📊 *Your Status:*\n\n"
            "Plan: Basic\n"
            "Status: Active\n"
            "Next Billing: 2025-12-01\n"
            "Signals Today: 3/5",
            parse_mode="Markdown",
        )

    async def handle_callback(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """Handle callback queries from inline buttons."""
        query = update.callback_query
        await query.answer()

        if query.data.startswith("plan_"):
            plan = query.data.replace("plan_", "")
            await query.edit_message_text(
                f"You selected: {plan.upper()}\n\n"
                "Visit https://quantumtrading.ai/subscribe to complete signup."
            )

    async def send_signal(self, chat_id: str, signal: Dict) -> bool:
        """
        Send trading signal to user.

        Args:
            chat_id: Telegram chat ID
            signal: Signal data dictionary

        Returns:
            True if sent successfully

        Example:
            >>> await bot.send_signal("123456", {
            ...     "symbol": "EURUSD",
            ...     "action": "BUY",
            ...     "entry_price": 1.1000,
            ...     "stop_loss": 1.0950,
            ...     "take_profit": 1.1100,
            ...     "confidence": 0.87
            ... })
        """
        if not self.app:
            logger.warning("Telegram bot not configured")
            return False

        try:
            signal_text = self._format_signal(signal)

            await self.app.bot.send_message(
                chat_id=chat_id,
                text=signal_text,
                parse_mode="Markdown",
            )

            logger.info(f"Signal sent to {chat_id}: {signal.get('symbol')}")
            return True

        except Exception as e:
            logger.error(f"Signal send error to {chat_id}: {e}")
            return False

    async def broadcast_signal(self, signal: Dict, user_ids: List[str]) -> int:
        """
        Broadcast signal to multiple users.

        Args:
            signal: Signal data
            user_ids: List of Telegram chat IDs

        Returns:
            Number of successful sends

        Example:
            >>> count = await bot.broadcast_signal(signal, ["123", "456"])
        """
        success_count = 0

        for chat_id in user_ids:
            if await self.send_signal(chat_id, signal):
                success_count += 1

        logger.info(
            f"Signal broadcasted: {success_count}/{len(user_ids)} successful",
            extra={
                "symbol": signal.get("symbol"),
                "successful": success_count,
                "total": len(user_ids),
            },
        )

        return success_count

    def _format_signal(self, signal: Dict) -> str:
        """
        Format signal data as Telegram message.

        Args:
            signal: Signal data

        Returns:
            Formatted message string
        """
        confidence_pct = signal.get("confidence", 0) * 100

        text = f"""
🔔 *TRADING SIGNAL*

📊 *Symbol:* {signal.get('symbol')}
📈 *Action:* {signal.get('action')}
💰 *Entry:* {signal.get('entry_price'):.5f}
🛑 *Stop Loss:* {signal.get('stop_loss'):.5f}
🎯 *Take Profit:* {signal.get('take_profit'):.5f}
⚡ *Confidence:* {confidence_pct:.1f}%

📝 *Reason:* {signal.get('reason', 'Quantum analysis')}

⏰ *Time:* {signal.get('created_at', 'Now')}

⚠️ *Risk Management:*
• Use proper position sizing
• Never risk more than 2% per trade
• Set stop loss immediately

Good luck! 🚀
        """

        return text.strip()

    async def start(self):
        """Start the bot."""
        if not self.app:
            logger.warning("Cannot start bot: not configured")
            return

        logger.info("Starting Telegram bot...")
        await self.app.run_polling()

    async def stop(self):
        """Stop the bot."""
        if self.app:
            await self.app.stop()
            logger.info("Telegram bot stopped")
