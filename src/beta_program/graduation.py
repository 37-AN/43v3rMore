"""Beta tester graduation and conversion to paid customers."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from uuid import uuid4
from loguru import logger

from ..database.queries import UserQueries, SubscriptionQueries
from ..communication.email import EmailService
from ..communication.telegram import TelegramBot
from ..payments.subscriptions import SubscriptionManager


class BetaGraduation:
    """
    Handle beta tester graduation to paid customers.

    Handles:
    - Success criteria evaluation
    - Discount code generation
    - Conversion emails and onboarding
    - Payment setup assistance
    - Referral program
    - Lifetime benefits for successful beta testers
    """

    def __init__(self):
        """Initialize beta graduation manager."""
        self.users = UserQueries()
        self.subscriptions = SubscriptionQueries()
        self.subscription_manager = SubscriptionManager()
        self.email = EmailService()
        self.telegram = TelegramBot()

        # Success criteria thresholds
        self.success_criteria = {
            "min_feedback_submissions": 3,  # At least 3 feedback submissions
            "min_engagement_rate": 0.70,  # 70% engagement
            "min_survey_completion": 3,  # Complete 3 of 4 weekly surveys
            "min_days_active": 21,  # Active for at least 3 weeks
        }

        # Graduation rewards
        self.rewards = {
            "successful_beta": {
                "discount": 0.50,  # 50% lifetime discount
                "is_lifetime": True,
                "bonus_months": 1,
                "referral_credits": 3,
            },
            "participated_beta": {
                "discount": 0.30,  # 30% for 6 months
                "is_lifetime": False,
                "duration_months": 6,
                "referral_credits": 1,
            },
        }

        logger.info("Beta graduation manager initialized")

    def evaluate_beta_success(self, user_id: str) -> Dict:
        """
        Evaluate beta tester success based on criteria.

        Args:
            user_id: Beta tester ID

        Returns:
            Evaluation results with success status and details

        Example:
            >>> graduation = BetaGraduation()
            >>> result = graduation.evaluate_beta_success("beta_001")
            >>> print(f"Success: {result['is_successful']}")
            >>> print(f"Criteria Met: {result['criteria_met']}/4")
        """
        try:
            # Get beta tester metrics
            metrics = self._get_beta_metrics(user_id)

            # Evaluate each criterion
            criteria_results = {}

            # 1. Feedback submissions
            criteria_results['feedback'] = {
                "met": metrics['feedback_count'] >= self.success_criteria['min_feedback_submissions'],
                "value": metrics['feedback_count'],
                "required": self.success_criteria['min_feedback_submissions'],
            }

            # 2. Engagement rate
            criteria_results['engagement'] = {
                "met": metrics['engagement_rate'] >= self.success_criteria['min_engagement_rate'],
                "value": metrics['engagement_rate'],
                "required": self.success_criteria['min_engagement_rate'],
            }

            # 3. Survey completion
            criteria_results['surveys'] = {
                "met": metrics['surveys_completed'] >= self.success_criteria['min_survey_completion'],
                "value": metrics['surveys_completed'],
                "required": self.success_criteria['min_survey_completion'],
            }

            # 4. Days active
            criteria_results['days_active'] = {
                "met": metrics['days_active'] >= self.success_criteria['min_days_active'],
                "value": metrics['days_active'],
                "required": self.success_criteria['min_days_active'],
            }

            # Calculate overall success
            criteria_met = sum(1 for c in criteria_results.values() if c['met'])
            is_successful = criteria_met >= 3  # Must meet at least 3 of 4 criteria

            result = {
                "user_id": user_id,
                "is_successful": is_successful,
                "criteria_met": criteria_met,
                "criteria_total": len(criteria_results),
                "criteria_details": criteria_results,
                "reward_tier": "successful_beta" if is_successful else "participated_beta",
                "metrics": metrics,
            }

            logger.info(
                f"Beta evaluation: {user_id} - {'SUCCESSFUL' if is_successful else 'PARTICIPATED'} "
                f"({criteria_met}/4 criteria met)"
            )

            return result

        except Exception as e:
            logger.error(f"Beta evaluation error: {e}")
            return {
                "user_id": user_id,
                "is_successful": False,
                "error": str(e),
            }

    def _get_beta_metrics(self, user_id: str) -> Dict:
        """Get beta tester metrics from database."""
        # In production, query from database
        return {
            "feedback_count": 4,
            "engagement_rate": 0.88,
            "surveys_completed": 4,
            "days_active": 28,
            "signals_received": 142,
            "signals_acted_on": 89,
            "win_rate": 0.96,
            "total_profit": 2180.50,
        }

    def generate_discount_code(
        self,
        user_id: str,
        reward_tier: str
    ) -> Dict:
        """
        Generate discount code for beta graduate.

        Args:
            user_id: Beta tester ID
            reward_tier: Reward tier (successful_beta or participated_beta)

        Returns:
            Discount code details
        """
        try:
            reward = self.rewards[reward_tier]

            code = f"BETA-{user_id.upper()}-{uuid4().hex[:8].upper()}"

            discount = {
                "code": code,
                "user_id": user_id,
                "discount_percentage": reward['discount'] * 100,
                "is_lifetime": reward.get('is_lifetime', False),
                "duration_months": reward.get('duration_months'),
                "bonus_months": reward.get('bonus_months', 0),
                "referral_credits": reward.get('referral_credits', 0),
                "created_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "status": "active",
            }

            logger.info(
                f"Discount code generated: {code} for {user_id} "
                f"({discount['discount_percentage']}% {'lifetime' if discount['is_lifetime'] else 'limited'})"
            )

            return discount

        except Exception as e:
            logger.error(f"Discount code generation error: {e}")
            return {}

    def graduate_beta_tester(self, user_id: str) -> Dict:
        """
        Complete beta graduation process.

        Args:
            user_id: Beta tester ID

        Returns:
            Graduation results with discount code and next steps

        Example:
            >>> graduation = BetaGraduation()
            >>> result = graduation.graduate_beta_tester("beta_001")
            >>> print(f"Discount Code: {result['discount_code']}")
            >>> print(f"Discount: {result['discount_percentage']}%")
        """
        try:
            # Evaluate beta success
            evaluation = self.evaluate_beta_success(user_id)

            if not evaluation.get('is_successful') and evaluation.get('criteria_met', 0) == 0:
                logger.warning(f"Beta tester {user_id} did not participate enough")
                return {
                    "status": "ineligible",
                    "message": "Insufficient beta participation",
                }

            # Generate discount code
            reward_tier = evaluation['reward_tier']
            discount = self.generate_discount_code(user_id, reward_tier)

            # Send graduation email
            email_sent = self._send_graduation_email(
                user_id,
                evaluation,
                discount
            )

            # Create referral credits
            referral_credits = self._create_referral_credits(
                user_id,
                discount['referral_credits']
            )

            result = {
                "status": "graduated",
                "user_id": user_id,
                "is_successful": evaluation['is_successful'],
                "criteria_met": evaluation['criteria_met'],
                "discount_code": discount['code'],
                "discount_percentage": discount['discount_percentage'],
                "is_lifetime_discount": discount['is_lifetime'],
                "bonus_months": discount['bonus_months'],
                "referral_credits": referral_credits['count'],
                "email_sent": email_sent,
                "next_steps": self._get_next_steps(evaluation['is_successful']),
            }

            logger.info(f"Beta tester graduated: {user_id} - {reward_tier}")

            return result

        except Exception as e:
            logger.error(f"Beta graduation error: {e}")
            return {
                "status": "error",
                "error": str(e),
            }

    def _send_graduation_email(
        self,
        user_id: str,
        evaluation: Dict,
        discount: Dict
    ) -> bool:
        """Send graduation email with discount code."""
        try:
            is_successful = evaluation['is_successful']
            user_email = self._get_user_email(user_id)

            if is_successful:
                subject = "🎉 You're a Quantum Trading AI Success Story!"

                body = f"""
                <h1>Congratulations, Champion! 🏆</h1>

                <p>You've completed the beta program as a <strong>successful beta tester</strong>!</p>

                <h2>Your Beta Impact:</h2>
                <ul>
                    <li>✅ Feedback Submissions: {evaluation['criteria_details']['feedback']['value']}</li>
                    <li>✅ Engagement Rate: {evaluation['criteria_details']['engagement']['value']:.0%}</li>
                    <li>✅ Surveys Completed: {evaluation['criteria_details']['surveys']['value']}/4</li>
                    <li>✅ Days Active: {evaluation['criteria_details']['days_active']['value']}</li>
                </ul>

                <h2>Your Exclusive Rewards:</h2>
                <div style="background:#f0f9ff;border-left:4px solid #00c853;padding:20px;margin:20px 0;">
                    <h3>🎁 50% LIFETIME Discount</h3>
                    <p style="font-size:24px;font-weight:bold;color:#00c853;margin:10px 0;">
                        {discount['code']}
                    </p>
                    <p><strong>Lifetime benefit</strong> - use this code for 50% off every month, forever!</p>
                </div>

                <h3>Additional Rewards:</h3>
                <ul>
                    <li>🎁 {discount['bonus_months']} month free subscription</li>
                    <li>🎫 {discount['referral_credits']} referral credits (R500 each)</li>
                    <li>⭐ Beta Champion badge on your profile</li>
                    <li>📊 Early access to new features</li>
                    <li>🎯 Priority support forever</li>
                </ul>

                <h2>Ready to Continue?</h2>
                <p><a href="https://quantumtrading.ai/graduate?code={discount['code']}" style="background:#00c853;color:white;padding:15px 40px;text-decoration:none;border-radius:5px;display:inline-block;margin:20px 0;font-size:18px;">Activate My Discount</a></p>

                <p><strong>Code expires in 30 days</strong> - activate today!</p>

                <p>Thank you for being part of our journey. Your feedback helped shape Quantum Trading AI!</p>

                <p>To the moon! 🚀<br>
                The Quantum Trading AI Team</p>
                """

            else:
                subject = "🎊 Thank You for Beta Testing - Special Offer Inside!"

                body = f"""
                <h1>Thank You for Beta Testing!</h1>

                <p>Your participation in the Quantum Trading AI beta program is greatly appreciated!</p>

                <h2>Your Beta Journey:</h2>
                <ul>
                    <li>Feedback Submissions: {evaluation['criteria_details']['feedback']['value']}</li>
                    <li>Engagement Rate: {evaluation['criteria_details']['engagement']['value']:.0%}</li>
                    <li>Surveys Completed: {evaluation['criteria_details']['surveys']['value']}/4</li>
                    <li>Days Active: {evaluation['criteria_details']['days_active']['value']}</li>
                </ul>

                <h2>Your Special Offer:</h2>
                <div style="background:#f0f9ff;border-left:4px solid #0091ea;padding:20px;margin:20px 0;">
                    <h3>💙 30% Discount for 6 Months</h3>
                    <p style="font-size:24px;font-weight:bold;color:#0091ea;margin:10px 0;">
                        {discount['code']}
                    </p>
                    <p>Save 30% on your subscription for the first 6 months!</p>
                </div>

                <h3>Additional Benefits:</h3>
                <ul>
                    <li>🎫 {discount['referral_credits']} referral credit (R500 value)</li>
                    <li>⭐ Beta Tester badge on your profile</li>
                    <li>📰 Exclusive newsletter with trading tips</li>
                </ul>

                <h2>Continue Your Trading Success:</h2>
                <p><a href="https://quantumtrading.ai/graduate?code={discount['code']}" style="background:#0091ea;color:white;padding:15px 40px;text-decoration:none;border-radius:5px;display:inline-block;margin:20px 0;font-size:18px;">Claim My Discount</a></p>

                <p><strong>Code expires in 30 days</strong> - don't miss out!</p>

                <p>Best regards,<br>
                The Quantum Trading AI Team</p>
                """

            return self.email.send_email(
                to_email=user_email,
                subject=subject,
                html_content=body
            )

        except Exception as e:
            logger.error(f"Graduation email error: {e}")
            return False

    def _create_referral_credits(self, user_id: str, count: int) -> Dict:
        """Create referral credits for beta graduate."""
        try:
            credits = {
                "user_id": user_id,
                "count": count,
                "value_per_credit": 500,  # R500
                "total_value": count * 500,
                "expires_at": (datetime.utcnow() + timedelta(days=365)).isoformat(),
            }

            # In production, store in database

            logger.info(f"Created {count} referral credits for {user_id}")
            return credits

        except Exception as e:
            logger.error(f"Referral credits error: {e}")
            return {"count": 0, "total_value": 0}

    def _get_next_steps(self, is_successful: bool) -> List[str]:
        """Get next steps for beta graduate."""
        if is_successful:
            return [
                "Click 'Activate My Discount' to set up your paid subscription",
                "Choose your plan (Pro or Premium)",
                "Enter your discount code at checkout",
                "Set up your payment method (PayFast)",
                "Continue receiving 95%+ accurate signals",
                "Share your referral link to earn R500 credits",
            ]
        else:
            return [
                "Click 'Claim My Discount' to continue",
                "Choose your plan (Basic, Pro, or Premium)",
                "Enter your discount code at checkout",
                "Set up your payment method (PayFast)",
                "Start your discounted subscription",
            ]

    def _get_user_email(self, user_id: str) -> str:
        """Get user email from database."""
        # In production, query database
        return f"{user_id}@example.com"

    def batch_graduate_beta_testers(self) -> Dict:
        """
        Graduate all beta testers at end of beta period.

        Returns:
            Batch graduation results
        """
        try:
            # Get all beta testers
            # In production, query from database
            beta_testers = [
                "beta_001", "beta_002", "beta_003", "beta_004", "beta_005",
                "beta_006", "beta_007", "beta_008", "beta_009", "beta_010",
            ]

            results = {
                "successful": [],
                "participated": [],
                "ineligible": [],
            }

            for user_id in beta_testers:
                graduation = self.graduate_beta_tester(user_id)

                if graduation['status'] == "graduated":
                    if graduation['is_successful']:
                        results['successful'].append(user_id)
                    else:
                        results['participated'].append(user_id)
                else:
                    results['ineligible'].append(user_id)

            summary = {
                "total_testers": len(beta_testers),
                "successful_count": len(results['successful']),
                "participated_count": len(results['participated']),
                "ineligible_count": len(results['ineligible']),
                "conversion_rate": (len(results['successful']) + len(results['participated'])) / len(beta_testers),
                "results": results,
            }

            logger.info(
                f"Batch graduation completed: {summary['successful_count']} successful, "
                f"{summary['participated_count']} participated, "
                f"{summary['ineligible_count']} ineligible"
            )

            return summary

        except Exception as e:
            logger.error(f"Batch graduation error: {e}")
            return {}

    def track_conversion(self, user_id: str, plan: str) -> Dict:
        """
        Track beta-to-paid conversion.

        Args:
            user_id: Beta tester ID
            plan: Plan they converted to

        Returns:
            Conversion tracking data
        """
        try:
            conversion = {
                "user_id": user_id,
                "plan": plan,
                "converted_at": datetime.utcnow().isoformat(),
                "source": "beta_program",
                "discount_applied": True,
            }

            # In production, store in database
            # Track in analytics

            logger.info(f"Beta conversion tracked: {user_id} → {plan}")
            return conversion

        except Exception as e:
            logger.error(f"Conversion tracking error: {e}")
            return {}

    def get_conversion_stats(self) -> Dict:
        """Get beta-to-paid conversion statistics."""
        # In production, query from database
        return {
            "total_beta_testers": 10,
            "conversions": 8,
            "conversion_rate": 0.80,  # 80%
            "successful_testers": 7,
            "avg_ltv_successful": 12000,  # R12K lifetime value
            "avg_ltv_participated": 3600,  # R3.6K lifetime value
            "total_referral_value": 4000,  # R4K in referrals
        }
