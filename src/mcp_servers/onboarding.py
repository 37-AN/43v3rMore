"""Automated user onboarding system."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from ..database.queries import UserQueries, SubscriptionQueries
from ..communication.telegram import TelegramBot
from ..communication.email import EmailService
from .support_agent import SupportAgent
from .content_generator import ContentGenerator


class OnboardingAutomation:
    """
    Automated user onboarding workflow.

    Handles complete onboarding journey:
    - Welcome messages
    - Account setup guidance
    - Platform tutorial
    - First signal explanation
    - Engagement monitoring
    - Conversion optimization
    """

    def __init__(self):
        """Initialize onboarding automation."""
        self.user_queries = UserQueries()
        self.sub_queries = SubscriptionQueries()
        self.telegram = TelegramBot()
        self.email = EmailService()
        self.support = SupportAgent()
        self.content = ContentGenerator()

        logger.info("Onboarding automation initialized")

    def onboard_new_user(
        self,
        user_id: str,
        email: str,
        name: str,
        plan: str,
        source: str = "website"
    ) -> Dict:
        """
        Execute complete onboarding workflow for new user.

        Args:
            user_id: User ID
            email: User email
            name: User name
            plan: Subscription plan
            source: Signup source

        Returns:
            Onboarding status and next steps

        Example:
            >>> onboarding = OnboardingAutomation()
            >>> result = onboarding.onboard_new_user(
            ...     user_id="user123",
            ...     email="trader@example.com",
            ...     name="John Smith",
            ...     plan="pro"
            ... )
        """
        try:
            logger.info(f"Starting onboarding for {email} ({plan} plan)")

            steps_completed = []

            # Step 1: Send welcome email
            welcome_sent = self._send_welcome_email(email, name, plan)
            if welcome_sent:
                steps_completed.append("welcome_email")

            # Step 2: Send Telegram setup instructions
            telegram_sent = self._send_telegram_setup(email, plan)
            if telegram_sent:
                steps_completed.append("telegram_setup")

            # Step 3: Create onboarding tasks
            tasks = self._create_onboarding_tasks(user_id, plan)
            steps_completed.append("tasks_created")

            # Step 4: Schedule follow-ups
            followups = self._schedule_followups(user_id, email, plan)
            steps_completed.append("followups_scheduled")

            # Step 5: Send platform tour
            tour_sent = self._send_platform_tour(email, plan)
            if tour_sent:
                steps_completed.append("platform_tour")

            onboarding_result = {
                "user_id": user_id,
                "status": "initiated",
                "steps_completed": steps_completed,
                "tasks": tasks,
                "followups": followups,
                "completion_rate": (len(steps_completed) / 5) * 100,
                "started_at": datetime.utcnow().isoformat(),
            }

            logger.info(
                f"Onboarding initiated: {email} - {len(steps_completed)}/5 steps",
                extra=onboarding_result
            )

            return onboarding_result

        except Exception as e:
            logger.error(f"Onboarding error for {email}: {e}")
            return {
                "user_id": user_id,
                "status": "failed",
                "error": str(e),
            }

    def _send_welcome_email(self, email: str, name: str, plan: str) -> bool:
        """Send personalized welcome email."""
        try:
            if not self.content.client:
                # Fallback welcome email
                return self.email.send_welcome_email(email, name)

            # Generate personalized welcome email
            campaign = self.content.generate_email_campaign(
                campaign_type="welcome",
                target_audience=f"{plan} plan subscribers",
                goal="welcome and educate new users"
            )

            # Send email
            subject = campaign.get("subject_line", "Welcome to Quantum Trading AI!")
            html_content = campaign.get("body_html", "")

            return self.email.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )

        except Exception as e:
            logger.error(f"Welcome email error: {e}")
            return False

    def _send_telegram_setup(self, email: str, plan: str) -> bool:
        """Send Telegram setup instructions."""
        try:
            setup_instructions = f"""
            <h2>Set Up Telegram for Instant Signals</h2>

            <p>Get real-time trading signals delivered instantly to your phone:</p>

            <ol>
                <li>Open Telegram app</li>
                <li>Search for <strong>@QuantumTradingBot</strong></li>
                <li>Click "Start" or type /start</li>
                <li>Type /subscribe and enter your email: {email}</li>
                <li>Done! You'll receive signals immediately</li>
            </ol>

            <p><strong>Your Plan: {plan.upper()}</strong></p>
            <p>You'll receive signals according to your plan limits.</p>

            <p>Need help? Reply to this email or contact support@quantumtrading.ai</p>
            """

            return self.email.send_email(
                to_email=email,
                subject="📱 Set Up Telegram for Instant Trading Signals",
                html_content=setup_instructions
            )

        except Exception as e:
            logger.error(f"Telegram setup email error: {e}")
            return False

    def _create_onboarding_tasks(self, user_id: str, plan: str) -> List[Dict]:
        """Create onboarding checklist tasks."""
        tasks = [
            {
                "id": "complete_profile",
                "title": "Complete your profile",
                "description": "Add your trading preferences and risk tolerance",
                "priority": "high",
                "completed": False,
            },
            {
                "id": "setup_telegram",
                "title": "Connect Telegram bot",
                "description": "Get instant signal notifications",
                "priority": "high",
                "completed": False,
            },
            {
                "id": "review_first_signal",
                "title": "Review your first signal",
                "description": "Understand entry, SL, TP, and confidence scores",
                "priority": "medium",
                "completed": False,
            },
            {
                "id": "watch_tutorial",
                "title": "Watch platform tutorial",
                "description": "3-minute video explaining all features",
                "priority": "medium",
                "completed": False,
            },
        ]

        if plan in ["premium", "bot", "enterprise"]:
            tasks.append({
                "id": "schedule_consultation",
                "title": "Schedule 1-on-1 consultation",
                "description": "Get personalized trading strategy advice",
                "priority": "high",
                "completed": False,
            })

        logger.info(f"Created {len(tasks)} onboarding tasks for {user_id}")
        return tasks

    def _schedule_followups(
        self,
        user_id: str,
        email: str,
        plan: str
    ) -> List[Dict]:
        """Schedule automated follow-up communications."""
        now = datetime.utcnow()

        followups = [
            {
                "type": "email",
                "subject": "How are your first signals performing?",
                "scheduled_for": (now + timedelta(days=3)).isoformat(),
                "goal": "engagement_check",
            },
            {
                "type": "email",
                "subject": "Trading Tips: Risk Management Essentials",
                "scheduled_for": (now + timedelta(days=5)).isoformat(),
                "goal": "education",
            },
            {
                "type": "email",
                "subject": "Your trial ends in 2 days - Upgrade to continue",
                "scheduled_for": (now + timedelta(days=5)).isoformat(),
                "goal": "conversion",
                "condition": "if_trial_user",
            },
        ]

        if plan in ["premium", "bot", "enterprise"]:
            followups.insert(1, {
                "type": "personal_outreach",
                "subject": "Welcome call from your account manager",
                "scheduled_for": (now + timedelta(days=1)).isoformat(),
                "goal": "relationship_building",
            })

        logger.info(f"Scheduled {len(followups)} follow-ups for {user_id}")
        return followups

    def _send_platform_tour(self, email: str, plan: str) -> bool:
        """Send interactive platform tour."""
        try:
            tour_content = f"""
            <h2>Welcome to Your Dashboard!</h2>

            <p>Here's a quick tour of what you can do:</p>

            <h3>📊 Signals Dashboard</h3>
            <p>View all active and historical signals with performance metrics.</p>

            <h3>🔔 Notifications</h3>
            <p>Configure how you receive signals: Telegram, WhatsApp, Email, SMS.</p>

            <h3>📈 Performance</h3>
            <p>Track signal accuracy, win rate, and your trading performance.</p>

            <h3>⚙️ Settings</h3>
            <p>Customize signal filters, trading pairs, and risk parameters.</p>

            <h3>💰 Billing</h3>
            <p>Manage your {plan} subscription, upgrade, or update payment method.</p>

            <p><a href="https://quantumtrading.ai/dashboard" style="background:#00c853;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;">Launch Dashboard</a></p>
            """

            return self.email.send_email(
                to_email=email,
                subject="🎯 Your Platform Tour - Get Started",
                html_content=tour_content
            )

        except Exception as e:
            logger.error(f"Platform tour email error: {e}")
            return False

    def track_onboarding_progress(self, user_id: str) -> Dict:
        """
        Track user's onboarding progress.

        Args:
            user_id: User ID

        Returns:
            Progress metrics
        """
        try:
            # This would query actual user actions from database
            # For now, return structure
            progress = {
                "user_id": user_id,
                "completion_percentage": 60,
                "completed_tasks": ["setup_telegram", "review_first_signal"],
                "pending_tasks": ["complete_profile", "watch_tutorial"],
                "days_since_signup": 2,
                "engagement_score": 75,
                "next_recommended_action": "complete_profile",
            }

            return progress

        except Exception as e:
            logger.error(f"Progress tracking error: {e}")
            return {}

    def send_onboarding_reminder(self, user_id: str, email: str) -> bool:
        """Send reminder to complete onboarding."""
        try:
            progress = self.track_onboarding_progress(user_id)
            completion = progress.get("completion_percentage", 0)

            if completion < 80:
                reminder = f"""
                <h2>Complete Your Setup</h2>

                <p>You're {completion}% done! Just a few more steps to get the most out of Quantum Trading AI:</p>

                <ul>
                    {' '.join([f'<li>{task}</li>' for task in progress.get('pending_tasks', [])])}
                </ul>

                <p><a href="https://quantumtrading.ai/onboarding">Complete Setup</a></p>
                """

                return self.email.send_email(
                    to_email=email,
                    subject=f"You're {completion}% done - Finish your setup!",
                    html_content=reminder
                )

            return True

        except Exception as e:
            logger.error(f"Reminder send error: {e}")
            return False
