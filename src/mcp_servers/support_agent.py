"""Customer support automation using Claude AI."""

from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
from loguru import logger

from ..utils.config import get_settings

settings = get_settings()


class SupportAgent:
    """
    AI-powered customer support agent using Claude.

    Handles:
    - Initial inquiries
    - Technical support
    - Subscription questions
    - Trading signal explanations
    - Account management
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize support agent."""
        self.api_key = api_key or settings.anthropic_api_key

        if not self.api_key:
            logger.warning("Anthropic API key not configured")
            self.client = None
            return

        try:
            self.client = Anthropic(api_key=self.api_key)
            self.conversation_history = {}
            logger.info("Support agent initialized")
        except Exception as e:
            logger.error(f"Support agent error: {e}")
            self.client = None

    def handle_inquiry(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Handle customer inquiry with AI-powered response.

        Args:
            user_id: User identifier
            message: Customer message
            context: Additional context (user plan, subscription status, etc.)

        Returns:
            Response dictionary with answer and metadata
        """
        if not self.client:
            return self._fallback_response(message)

        try:
            # Build conversation context
            prompt = self._build_support_prompt(user_id, message, context)

            # Get conversation history
            history = self.conversation_history.get(user_id, [])

            # Prepare messages for Claude
            messages = history + [{
                "role": "user",
                "content": message
            }]

            # Call Claude API
            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=2048,
                system=prompt,
                messages=messages
            )

            # Extract response
            assistant_message = response.content[0].text

            # Update conversation history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": assistant_message})
            self.conversation_history[user_id] = history[-10:]  # Keep last 10 messages

            # Parse response for actions
            actions = self._extract_actions(assistant_message)

            result = {
                "response": assistant_message,
                "actions": actions,
                "confidence": "high" if len(assistant_message) > 50 else "medium",
                "timestamp": datetime.utcnow().isoformat(),
                "handled_by": "ai",
            }

            logger.info(
                f"Support inquiry handled: {user_id}",
                extra={"user_id": user_id, "actions": actions}
            )

            return result

        except Exception as e:
            logger.error(f"Support inquiry error: {e}")
            return self._fallback_response(message)

    def _build_support_prompt(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict]
    ) -> str:
        """Build system prompt for support agent."""
        user_plan = context.get('plan', 'basic') if context else 'basic'
        user_status = context.get('status', 'active') if context else 'active'

        return f"""You are a professional customer support agent for Quantum Trading AI, a South African trading signal service using quantum computing.

USER CONTEXT:
- User ID: {user_id}
- Subscription Plan: {user_plan}
- Account Status: {user_status}

YOUR ROLE:
- Provide helpful, accurate, and professional support
- Be empathetic and understanding
- Solve problems efficiently
- Escalate complex issues when needed
- Always maintain a friendly, professional tone

COMPANY INFORMATION:
- Service: AI-powered trading signals using quantum computing
- Target Accuracy: 95%+
- Channels: Telegram, WhatsApp, Email, SMS
- Payment: PayFast (ZAR currency)
- Plans: Basic (R500), Pro (R1000), Premium (R2000), Bot (R3000), Enterprise (R10K)

SUBSCRIPTION PLANS:
- Basic: 5 signals/day, major pairs, Telegram + Email
- Pro: 10 signals/day, all pairs, all channels, priority support
- Premium: Unlimited signals, all pairs, 1-on-1 support, custom analysis
- Bot License: Automated trading bot, 24/7 execution
- Enterprise: Custom solutions, API access, dedicated support

COMMON TOPICS:
1. Signal Explanations: Explain entry, SL, TP, confidence scores
2. Subscription Management: Upgrades, cancellations, billing
3. Technical Issues: Telegram bot, notifications, MT5 integration
4. Trading Questions: Risk management, position sizing, timing
5. Account Issues: Login, password reset, profile updates

RESPONSE GUIDELINES:
- Keep responses concise but complete
- Use bullet points for clarity
- Include specific numbers and examples
- Provide actionable next steps
- End with "Is there anything else I can help with?"

ACTIONS YOU CAN TRIGGER:
- [ESCALATE] - Transfer to human support
- [UPGRADE] - Suggest plan upgrade
- [REFUND] - Process refund request
- [TECHNICAL] - Create technical support ticket
- [DOCUMENTATION] - Share relevant docs/guides

If you recommend an action, include it in brackets like [UPGRADE] at the end of your response.

Remember: You represent a premium, professional service. Be helpful, knowledgeable, and customer-focused."""

    def _extract_actions(self, response: str) -> List[str]:
        """Extract action tags from response."""
        import re

        actions = []
        action_pattern = r'\[([A-Z_]+)\]'
        matches = re.findall(action_pattern, response)

        for action in matches:
            actions.append(action.lower())

        return actions

    def _fallback_response(self, message: str) -> Dict:
        """Fallback response when Claude is unavailable."""
        return {
            "response": "Thank you for contacting Quantum Trading AI support. "
                       "We've received your message and a team member will respond within 24 hours. "
                       "For urgent issues, please email support@quantumtrading.ai",
            "actions": ["create_ticket"],
            "confidence": "low",
            "timestamp": datetime.utcnow().isoformat(),
            "handled_by": "fallback",
        }

    def analyze_sentiment(self, message: str) -> Dict:
        """
        Analyze customer message sentiment.

        Args:
            message: Customer message

        Returns:
            Sentiment analysis results
        """
        if not self.client:
            return {"sentiment": "neutral", "confidence": 0.5}

        try:
            prompt = f"""Analyze the sentiment of this customer message.

Message: "{message}"

Provide a JSON response with:
{{
  "sentiment": "<positive|neutral|negative>",
  "confidence": <0.0-1.0>,
  "urgency": "<low|medium|high>",
  "emotion": "<specific emotion>",
  "priority": <1-5>
}}

Only output the JSON, no additional text."""

            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result_text = response.content[0].text
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1

            if json_start >= 0:
                return json.loads(result_text[json_start:json_end])

            return {"sentiment": "neutral", "confidence": 0.5}

        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {"sentiment": "neutral", "confidence": 0.5}

    def generate_faq_response(self, question: str) -> Optional[str]:
        """
        Generate FAQ response for common questions.

        Args:
            question: Customer question

        Returns:
            FAQ response or None
        """
        faqs = {
            "how do signals work": """Our signals provide complete trade setups:
• Entry Price: Where to enter the trade
• Stop Loss (SL): Risk management level
• Take Profit (TP): Target profit level
• Confidence: AI accuracy score (aim for 75%+)

Example: BUY EURUSD @ 1.1000, SL: 1.0950, TP: 1.1100, 87% confidence""",

            "how to subscribe": """To subscribe:
1. Visit our website or use /subscribe in Telegram
2. Choose your plan (Basic, Pro, Premium)
3. Complete payment via PayFast
4. Instant activation after payment confirmation

Free 7-day trial available on all plans!""",

            "what is risk management": """Risk Management Essentials:
• Never risk more than 2% per trade
• Always set stop loss immediately
• Use proper position sizing
• Don't overtrade (max 3-5 trades/day)
• Follow our signals' SL/TP levels

We include risk calculations in Pro+ plans.""",

            "how accurate are signals": """Our quantum AI targets 95%+ accuracy:
• Advanced QPE algorithms
• Real-time market analysis
• Backtested strategies
• Live performance tracking

Current performance available in your dashboard.""",
        }

        # Simple keyword matching
        question_lower = question.lower()
        for key, answer in faqs.items():
            if key in question_lower:
                return answer

        return None

    def clear_conversation_history(self, user_id: str) -> None:
        """Clear conversation history for a user."""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info(f"Cleared conversation history for {user_id}")
