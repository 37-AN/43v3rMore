"""Main MCP server orchestrator for business automation using Claude AI."""

from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from .lead_manager import LeadQualificationAgent
from .support_agent import SupportAgent
from .content_generator import ContentGenerator
from .onboarding import OnboardingAutomation
from .analytics import AnalyticsAgent
from ..utils.config import get_settings

settings = get_settings()


class BusinessAutomationServer:
    """
    Main orchestrator for all business automation.

    Coordinates:
    - Lead qualification and management
    - Customer support automation
    - Content generation
    - User onboarding
    - Analytics and reporting
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize business automation server.

        Args:
            api_key: Anthropic API key

        Example:
            >>> automation = BusinessAutomationServer()
            >>> result = automation.process_new_lead(lead_data)
        """
        self.api_key = api_key or settings.anthropic_api_key

        # Initialize all automation agents
        self.lead_agent = LeadQualificationAgent(self.api_key)
        self.support_agent = SupportAgent(self.api_key)
        self.content_generator = ContentGenerator(self.api_key)
        self.onboarding = OnboardingAutomation()
        self.analytics = AnalyticsAgent(self.api_key)

        logger.info("Business automation server initialized")

    def process_new_lead(self, lead_data: Dict) -> Dict:
        """
        Complete lead processing workflow.

        Args:
            lead_data: Lead information

        Returns:
            Processing results with next actions
        """
        try:
            # Step 1: Qualify lead
            qualification = self.lead_agent.qualify_lead(lead_data)

            # Step 2: Generate personalized welcome email
            if qualification['tier'] in ['hot', 'warm']:
                campaign = self.content_generator.generate_email_campaign(
                    campaign_type="lead_nurture",
                    target_audience=f"{qualification['tier']} lead",
                    goal="convert to trial user"
                )
            else:
                campaign = None

            # Step 3: Determine next actions
            next_actions = self.lead_agent.get_lead_recommendations(
                lead_score=qualification['score'],
                tier=qualification['tier']
            )

            result = {
                "lead_email": lead_data.get('email'),
                "qualification": qualification,
                "campaign": campaign,
                "next_actions": next_actions,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "processed",
            }

            logger.info(
                f"Lead processed: {lead_data.get('email')} - {qualification['tier']} ({qualification['score']}/100)",
                extra=result
            )

            return result

        except Exception as e:
            logger.error(f"Lead processing error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "lead_email": lead_data.get('email'),
            }

    def process_new_user(
        self,
        user_id: str,
        email: str,
        name: str,
        plan: str
    ) -> Dict:
        """
        Complete new user onboarding.

        Args:
            user_id: User ID
            email: Email address
            name: User name
            plan: Subscription plan

        Returns:
            Onboarding status
        """
        try:
            # Execute onboarding workflow
            onboarding_result = self.onboarding.onboard_new_user(
                user_id=user_id,
                email=email,
                name=name,
                plan=plan
            )

            logger.info(f"User onboarded: {email} ({plan})")
            return onboarding_result

        except Exception as e:
            logger.error(f"User onboarding error: {e}")
            return {"status": "error", "error": str(e)}

    def handle_support_inquiry(
        self,
        user_id: str,
        message: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Handle customer support inquiry.

        Args:
            user_id: User ID
            message: Support message
            context: User context

        Returns:
            Support response
        """
        try:
            response = self.support_agent.handle_inquiry(
                user_id=user_id,
                message=message,
                context=context
            )

            logger.info(f"Support inquiry handled: {user_id}")
            return response

        except Exception as e:
            logger.error(f"Support handling error: {e}")
            return {
                "response": "We're experiencing technical issues. Please email support@quantumtrading.ai",
                "status": "error",
            }

    def generate_marketing_content(
        self,
        content_type: str,
        **kwargs
    ) -> Dict:
        """
        Generate marketing content.

        Args:
            content_type: Type (email, social, blog, landing_page)
            **kwargs: Content-specific parameters

        Returns:
            Generated content
        """
        try:
            if content_type == "email":
                return self.content_generator.generate_email_campaign(
                    campaign_type=kwargs.get('campaign_type', 'newsletter'),
                    target_audience=kwargs.get('target_audience', 'all users'),
                    goal=kwargs.get('goal', 'engagement')
                )

            elif content_type == "social":
                return self.content_generator.generate_social_post(
                    platform=kwargs.get('platform', 'twitter'),
                    topic=kwargs.get('topic', 'trading signals'),
                    tone=kwargs.get('tone', 'professional')
                )

            elif content_type == "blog":
                return self.content_generator.generate_blog_article(
                    title=kwargs.get('title', 'Quantum Trading Guide'),
                    keywords=kwargs.get('keywords', ['trading', 'quantum', 'AI']),
                    target_length=kwargs.get('target_length', 1500)
                )

            elif content_type == "landing_page":
                return self.content_generator.generate_landing_page_copy(
                    page_goal=kwargs.get('page_goal', 'conversions'),
                    target_audience=kwargs.get('target_audience', 'traders')
                )

            else:
                return {"error": f"Unknown content type: {content_type}"}

        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return {"error": str(e)}

    def get_business_insights(self, report_type: str = "daily") -> Dict:
        """
        Get business analytics and insights.

        Args:
            report_type: Report type (daily, weekly)

        Returns:
            Analytics report
        """
        try:
            if report_type == "daily":
                return self.analytics.generate_daily_report()
            elif report_type == "weekly":
                return self.analytics.generate_weekly_report()
            else:
                return self.analytics.get_dashboard_summary()

        except Exception as e:
            logger.error(f"Analytics error: {e}")
            return {"error": str(e)}

    def run_automation_workflows(self) -> Dict:
        """
        Run all scheduled automation workflows.

        Returns:
            Workflow execution results
        """
        try:
            results = {
                "started_at": datetime.utcnow().isoformat(),
                "workflows_executed": [],
                "errors": [],
            }

            # Workflow 1: Daily analytics report
            try:
                report = self.analytics.generate_daily_report()
                results['workflows_executed'].append({
                    "workflow": "daily_analytics",
                    "status": "success",
                    "metrics_count": len(report.get('metrics', {})),
                })
            except Exception as e:
                results['errors'].append({"workflow": "daily_analytics", "error": str(e)})

            # Workflow 2: Lead scoring updates
            # (Would integrate with database queries)

            # Workflow 3: Onboarding follow-ups
            # (Would check scheduled follow-ups)

            results['completed_at'] = datetime.utcnow().isoformat()
            results['success_rate'] = len(results['workflows_executed']) / (len(results['workflows_executed']) + len(results['errors']))

            logger.info(
                f"Automation workflows completed: {len(results['workflows_executed'])} successful, {len(results['errors'])} errors"
            )

            return results

        except Exception as e:
            logger.error(f"Automation workflow error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat(),
            }

    def get_system_status(self) -> Dict:
        """
        Get automation system status.

        Returns:
            System status
        """
        return {
            "status": "operational",
            "components": {
                "lead_qualification": "active" if self.lead_agent.client else "unavailable",
                "customer_support": "active" if self.support_agent.client else "unavailable",
                "content_generation": "active" if self.content_generator.client else "unavailable",
                "onboarding": "active",
                "analytics": "active" if self.analytics.client else "unavailable",
            },
            "api_key_configured": self.api_key is not None,
            "checked_at": datetime.utcnow().isoformat(),
        }
