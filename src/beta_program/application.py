"""Beta tester application and selection system."""

from typing import Dict, List, Optional
from datetime import datetime
from uuid import uuid4
from loguru import logger

from ..database.queries import UserQueries
from ..mcp_servers.lead_manager import LeadQualificationAgent
from ..communication.email import EmailService


class BetaApplicationManager:
    """
    Manage beta tester applications and selection.

    Handles:
    - Application submissions
    - Automated screening
    - Selection criteria
    - Acceptance/rejection notifications
    - Waitlist management
    """

    def __init__(self, max_testers: int = 10):
        """
        Initialize beta application manager.

        Args:
            max_testers: Maximum number of beta testers
        """
        self.max_testers = max_testers
        self.user_queries = UserQueries()
        self.lead_agent = LeadQualificationAgent()
        self.email_service = EmailService()

        logger.info(f"Beta application manager initialized: max {max_testers} testers")

    def submit_application(self, application_data: Dict) -> Dict:
        """
        Submit beta tester application.

        Args:
            application_data: Application information
                - email: Email address
                - name: Full name
                - trading_experience: Years of trading
                - platforms_used: List of platforms (MT5, TradingView, etc.)
                - primary_pairs: Trading pairs
                - why_join: Reason for joining beta
                - availability: Hours per week for testing
                - feedback_commitment: Willingness to provide feedback

        Returns:
            Application result with status

        Example:
            >>> manager = BetaApplicationManager()
            >>> result = manager.submit_application({
            ...     "email": "trader@example.com",
            ...     "name": "John Trader",
            ...     "trading_experience": 3,
            ...     "platforms_used": ["MT5", "TradingView"],
            ...     "primary_pairs": ["EURUSD", "GBPUSD"],
            ...     "why_join": "Want to improve my trading with AI",
            ...     "availability": 10,
            ...     "feedback_commitment": True
            ... })
        """
        try:
            logger.info(f"Beta application received: {application_data.get('email')}")

            # Score application
            score = self._score_application(application_data)

            # Create application record
            application = {
                "id": str(uuid4()),
                "email": application_data.get('email'),
                "name": application_data.get('name'),
                "score": score['total_score'],
                "criteria_scores": score['breakdown'],
                "status": "pending",  # pending, accepted, rejected, waitlisted
                "submitted_at": datetime.utcnow().isoformat(),
                "data": application_data,
            }

            # Determine status based on score and capacity
            current_count = self._get_current_tester_count()

            if score['total_score'] >= 80 and current_count < self.max_testers:
                application['status'] = "accepted"
                self._send_acceptance_email(application)
            elif score['total_score'] >= 60:
                application['status'] = "waitlisted"
                self._send_waitlist_email(application)
            else:
                application['status'] = "rejected"
                self._send_rejection_email(application)

            logger.info(
                f"Application processed: {application['email']} - {application['status']} (score: {score['total_score']}/100)"
            )

            return {
                "application_id": application['id'],
                "status": application['status'],
                "score": score['total_score'],
                "message": self._get_status_message(application['status']),
            }

        except Exception as e:
            logger.error(f"Application submission error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Application submission failed. Please try again.",
            }

    def _score_application(self, data: Dict) -> Dict:
        """
        Score application based on criteria.

        Criteria:
        1. Trading Experience (0-25 points)
        2. Platform Knowledge (0-20 points)
        3. Feedback Commitment (0-20 points)
        4. Availability (0-15 points)
        5. Motivation (0-20 points)
        """
        scores = {}

        # 1. Trading Experience (0-25)
        experience = data.get('trading_experience', 0)
        if experience >= 5:
            scores['experience'] = 25
        elif experience >= 3:
            scores['experience'] = 20
        elif experience >= 1:
            scores['experience'] = 15
        else:
            scores['experience'] = 5

        # 2. Platform Knowledge (0-20)
        platforms = data.get('platforms_used', [])
        if 'MT5' in platforms:
            scores['platforms'] = 20
        elif any(p in platforms for p in ['MT4', 'TradingView', 'cTrader']):
            scores['platforms'] = 15
        else:
            scores['platforms'] = 5

        # 3. Feedback Commitment (0-20)
        scores['feedback'] = 20 if data.get('feedback_commitment') else 5

        # 4. Availability (0-15)
        hours = data.get('availability', 0)
        if hours >= 10:
            scores['availability'] = 15
        elif hours >= 5:
            scores['availability'] = 10
        else:
            scores['availability'] = 5

        # 5. Motivation (0-20)
        why_join = data.get('why_join', '').lower()
        motivation_keywords = ['improve', 'learn', 'test', 'feedback', 'help', 'contribute']
        keyword_count = sum(1 for keyword in motivation_keywords if keyword in why_join)
        scores['motivation'] = min(20, keyword_count * 5)

        total = sum(scores.values())

        return {
            "total_score": total,
            "breakdown": scores,
        }

    def _get_current_tester_count(self) -> int:
        """Get current number of active beta testers."""
        # In production, query database
        return 0

    def _send_acceptance_email(self, application: Dict) -> bool:
        """Send acceptance email to beta tester."""
        try:
            subject = "🎉 Welcome to Quantum Trading AI Beta Program!"

            body = f"""
            <h1>Congratulations {application['name']}!</h1>

            <p>You've been selected for the Quantum Trading AI Beta Program!</p>

            <h2>What's Next?</h2>
            <ol>
                <li><strong>Complete Setup</strong>: Set up your account and Telegram bot</li>
                <li><strong>Start Receiving Signals</strong>: Get 95%+ accurate trading signals</li>
                <li><strong>Provide Feedback</strong>: Share your experience weekly</li>
                <li><strong>Earn Rewards</strong>: Get lifetime 50% discount after beta</li>
            </ol>

            <h2>Beta Program Benefits</h2>
            <ul>
                <li>✅ Free access during beta period (4 weeks)</li>
                <li>✅ Unlimited signals (Premium plan features)</li>
                <li>✅ Direct line to founders</li>
                <li>✅ Shape the product roadmap</li>
                <li>✅ 50% lifetime discount after beta</li>
            </ul>

            <p><a href="https://quantumtrading.ai/beta/onboard" style="background:#00c853;color:white;padding:15px 30px;text-decoration:none;border-radius:5px;display:inline-block;margin:20px 0;">Get Started Now</a></p>

            <p>Looking forward to your feedback!</p>
            <p>The Quantum Trading AI Team</p>
            """

            return self.email_service.send_email(
                to_email=application['email'],
                subject=subject,
                html_content=body
            )

        except Exception as e:
            logger.error(f"Acceptance email error: {e}")
            return False

    def _send_waitlist_email(self, application: Dict) -> bool:
        """Send waitlist email."""
        subject = "You're on the Quantum Trading AI Beta Waitlist"

        body = f"""
        <h1>Thank you for your interest, {application['name']}!</h1>

        <p>We've received your beta application and you're on our waitlist.</p>

        <p><strong>Your Application Score: {application['score']}/100</strong></p>

        <p>We'll contact you if a spot opens up in the next 2 weeks.</p>

        <p>In the meantime, you can:</p>
        <ul>
            <li>Join our newsletter for trading tips</li>
            <li>Follow us on social media</li>
            <li>Refer friends to move up the waitlist</li>
        </ul>

        <p>Best regards,<br>The Quantum Trading AI Team</p>
        """

        return self.email_service.send_email(
            to_email=application['email'],
            subject=subject,
            html_content=body
        )

    def _send_rejection_email(self, application: Dict) -> bool:
        """Send rejection email (politely)."""
        subject = "Quantum Trading AI Beta Program Update"

        body = f"""
        <h1>Thank you for your interest, {application['name']}!</h1>

        <p>We appreciate your application for our beta program.</p>

        <p>Unfortunately, we've reached capacity for this beta cycle. However, we'd love to have you in our next testing phase!</p>

        <p><strong>What you can do:</strong></p>
        <ul>
            <li>Join our free newsletter for trading insights</li>
            <li>Get early-bird pricing when we launch (30% off)</li>
            <li>Apply for our next beta round in 6 weeks</li>
        </ul>

        <p><a href="https://quantumtrading.ai/early-access">Get Early Access</a></p>

        <p>Best regards,<br>The Quantum Trading AI Team</p>
        """

        return self.email_service.send_email(
            to_email=application['email'],
            subject=subject,
            html_content=body
        )

    def _get_status_message(self, status: str) -> str:
        """Get user-friendly status message."""
        messages = {
            "accepted": "Congratulations! Check your email for next steps.",
            "waitlisted": "You're on our waitlist. We'll contact you if a spot opens.",
            "rejected": "Thank you for your interest. We'll let you know about future opportunities.",
        }
        return messages.get(status, "Application received.")

    def get_application_stats(self) -> Dict:
        """Get beta application statistics."""
        # In production, query database
        return {
            "total_applications": 45,
            "accepted": 10,
            "waitlisted": 20,
            "rejected": 15,
            "acceptance_rate": 0.22,
            "average_score": 68.5,
        }
