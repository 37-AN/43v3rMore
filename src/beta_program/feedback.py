"""Feedback collection and management for beta testers."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from loguru import logger

from ..database.queries import AnalyticsQueries
from ..communication.email import EmailService
from ..communication.telegram import TelegramBot


class FeedbackCollector:
    """
    Collect and manage beta tester feedback.

    Handles:
    - Feedback submissions
    - Weekly surveys
    - Bug reports
    - Feature requests
    - Satisfaction tracking
    - Automated follow-ups
    """

    def __init__(self):
        """Initialize feedback collector."""
        self.analytics = AnalyticsQueries()
        self.email = EmailService()
        self.telegram = TelegramBot()

        logger.info("Feedback collector initialized")

    def submit_feedback(
        self,
        user_id: str,
        feedback_type: str,
        content: Dict
    ) -> Dict:
        """
        Submit feedback from beta tester.

        Args:
            user_id: Beta tester ID
            feedback_type: Type (general, bug, feature, satisfaction)
            content: Feedback content

        Returns:
            Submission confirmation

        Example:
            >>> collector = FeedbackCollector()
            >>> result = collector.submit_feedback(
            ...     user_id="beta_001",
            ...     feedback_type="bug",
            ...     content={
            ...         "title": "Telegram notifications delayed",
            ...         "description": "Signals arrive 2-3 minutes late",
            ...         "severity": "medium",
            ...         "steps_to_reproduce": "1. Subscribe to signals 2. Wait for signal 3. Check timestamp"
            ...     }
            ... )
        """
        try:
            feedback = {
                "id": str(uuid4()),
                "user_id": user_id,
                "type": feedback_type,
                "content": content,
                "status": "new",  # new, reviewed, in_progress, resolved, closed
                "priority": self._calculate_priority(feedback_type, content),
                "created_at": datetime.utcnow().isoformat(),
            }

            # Auto-categorize
            feedback['category'] = self._categorize_feedback(content)

            # Store in database
            self.analytics.track_event(
                event_type="beta_feedback_submitted",
                user_id=user_id,
                data=feedback
            )

            # Send confirmation
            self._send_feedback_confirmation(user_id, feedback)

            # Auto-escalate high priority
            if feedback['priority'] == "high":
                self._escalate_feedback(feedback)

            logger.info(
                f"Feedback submitted: {feedback_type} from {user_id}",
                extra={"feedback_id": feedback['id'], "priority": feedback['priority']}
            )

            return {
                "feedback_id": feedback['id'],
                "status": "submitted",
                "priority": feedback['priority'],
                "message": "Thank you! We'll review your feedback within 24 hours.",
            }

        except Exception as e:
            logger.error(f"Feedback submission error: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    def send_weekly_survey(self, user_id: str, week_number: int) -> bool:
        """
        Send weekly satisfaction survey to beta tester.

        Args:
            user_id: Beta tester ID
            week_number: Week number (1-4)

        Returns:
            True if sent successfully
        """
        try:
            survey_questions = self._get_weekly_questions(week_number)

            survey_link = f"https://quantumtrading.ai/beta/survey/{user_id}/week{week_number}"

            subject = f"📊 Week {week_number} Beta Feedback - Quantum Trading AI"

            body = f"""
            <h1>Week {week_number} Beta Feedback</h1>

            <p>Thank you for testing Quantum Trading AI! Your feedback is crucial.</p>

            <h2>This Week's Questions:</h2>
            <ol>
                {''.join([f'<li>{q}</li>' for q in survey_questions])}
            </ol>

            <p><strong>Takes only 3 minutes</strong></p>

            <p><a href="{survey_link}" style="background:#00c853;color:white;padding:15px 30px;text-decoration:none;border-radius:5px;display:inline-block;margin:20px 0;">Complete Survey</a></p>

            <p><strong>Bonus:</strong> Complete all 4 weekly surveys for an extra month free after launch!</p>

            <p>Best regards,<br>The Quantum Trading AI Team</p>
            """

            # Send via email
            return self.email.send_email(
                to_email=self._get_user_email(user_id),
                subject=subject,
                html_content=body
            )

        except Exception as e:
            logger.error(f"Weekly survey error: {e}")
            return False

    def _get_weekly_questions(self, week: int) -> List[str]:
        """Get week-specific survey questions."""
        base_questions = [
            "How satisfied are you with the signal accuracy? (1-5)",
            "How would you rate the signal delivery speed? (1-5)",
            "Have you encountered any bugs or issues?",
            "What feature would improve your experience most?",
        ]

        week_specific = {
            1: [
                "How easy was the onboarding process? (1-5)",
                "Did you successfully receive your first signal?",
            ],
            2: [
                "How many signals have you acted on?",
                "What's your win rate so far?",
            ],
            3: [
                "Would you recommend this to other traders? (1-5)",
                "What's the most valuable feature for you?",
            ],
            4: [
                "Will you continue using after beta? (Yes/No/Maybe)",
                "What pricing would you consider fair?",
            ],
        }

        return base_questions + week_specific.get(week, [])

    def _calculate_priority(self, feedback_type: str, content: Dict) -> str:
        """Calculate feedback priority."""
        if feedback_type == "bug":
            severity = content.get('severity', 'low')
            if severity == "critical":
                return "high"
            elif severity in ["high", "medium"]:
                return "medium"
            return "low"

        elif feedback_type == "feature":
            # Check if highly requested
            return "medium"

        elif feedback_type == "satisfaction":
            rating = content.get('rating', 5)
            if rating <= 2:
                return "high"  # Unhappy user
            return "low"

        return "medium"

    def _categorize_feedback(self, content: Dict) -> str:
        """Auto-categorize feedback."""
        text = str(content).lower()

        categories = {
            "accuracy": ["accuracy", "wrong", "signal", "incorrect", "loss"],
            "delivery": ["late", "delay", "telegram", "notification", "didn't receive"],
            "usability": ["difficult", "confusing", "hard to", "understand", "UI", "UX"],
            "performance": ["slow", "fast", "speed", "lag"],
            "feature_request": ["wish", "would be nice", "suggestion", "add", "feature"],
        }

        for category, keywords in categories.items():
            if any(keyword in text for keyword in keywords):
                return category

        return "general"

    def _send_feedback_confirmation(self, user_id: str, feedback: Dict) -> bool:
        """Send feedback confirmation to user."""
        try:
            message = f"""
Thank you for your feedback!

Feedback ID: {feedback['id']}
Type: {feedback['type']}
Priority: {feedback['priority']}

We'll review and respond within 24 hours.
            """

            # Send via Telegram if available
            telegram_id = self._get_user_telegram(user_id)
            if telegram_id:
                return self.telegram.send_message(telegram_id, message)

            return True

        except Exception as e:
            logger.error(f"Confirmation send error: {e}")
            return False

    def _escalate_feedback(self, feedback: Dict) -> None:
        """Escalate high-priority feedback."""
        logger.warning(
            f"HIGH PRIORITY FEEDBACK: {feedback['type']} from {feedback['user_id']}",
            extra=feedback
        )
        # In production, send to Slack/email/SMS

    def _get_user_email(self, user_id: str) -> str:
        """Get user email from database."""
        # In production, query database
        return f"{user_id}@example.com"

    def _get_user_telegram(self, user_id: str) -> Optional[str]:
        """Get user Telegram ID from database."""
        # In production, query database
        return None

    def get_feedback_summary(self, days: int = 7) -> Dict:
        """
        Get feedback summary for last N days.

        Args:
            days: Number of days to analyze

        Returns:
            Feedback statistics
        """
        try:
            # In production, query database
            summary = {
                "period_days": days,
                "total_feedback": 28,
                "by_type": {
                    "bug": 8,
                    "feature": 12,
                    "general": 5,
                    "satisfaction": 3,
                },
                "by_priority": {
                    "high": 3,
                    "medium": 15,
                    "low": 10,
                },
                "avg_satisfaction": 4.2,
                "response_rate": 0.93,  # 93% of feedback responded to
                "resolution_time_hours": 18.5,
            }

            return summary

        except Exception as e:
            logger.error(f"Feedback summary error: {e}")
            return {}

    def get_top_feature_requests(self, limit: int = 5) -> List[Dict]:
        """Get most requested features."""
        # In production, aggregate from database
        return [
            {"feature": "Mobile app", "votes": 8, "priority": "high"},
            {"feature": "Custom alert times", "votes": 6, "priority": "medium"},
            {"feature": "Historical performance chart", "votes": 5, "priority": "medium"},
            {"feature": "Risk calculator", "votes": 4, "priority": "low"},
            {"feature": "Multiple timeframes", "votes": 3, "priority": "low"},
        ]

    def schedule_feedback_requests(self) -> List[Dict]:
        """
        Schedule feedback requests for all beta testers.

        Returns:
            List of scheduled requests
        """
        try:
            # Get all beta testers
            # In production, query from database
            beta_testers = [
                {"id": "beta_001", "joined_date": "2025-11-10", "week": 1},
                {"id": "beta_002", "joined_date": "2025-11-10", "week": 1},
                # ... more testers
            ]

            scheduled = []
            for tester in beta_testers:
                # Calculate which week they're in
                joined = datetime.fromisoformat(tester['joined_date'])
                weeks_in = ((datetime.utcnow() - joined).days // 7) + 1

                if weeks_in <= 4:  # Beta is 4 weeks
                    # Schedule survey
                    survey_sent = self.send_weekly_survey(tester['id'], weeks_in)
                    scheduled.append({
                        "user_id": tester['id'],
                        "week": weeks_in,
                        "sent": survey_sent,
                    })

            logger.info(f"Scheduled {len(scheduled)} feedback requests")
            return scheduled

        except Exception as e:
            logger.error(f"Scheduling error: {e}")
            return []
