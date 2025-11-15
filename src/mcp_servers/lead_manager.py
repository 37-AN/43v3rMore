"""Lead qualification and management using Claude AI."""

from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
from loguru import logger

from ..utils.config import get_settings
from ..database.queries import AnalyticsQueries
from ..database.models import LeadScore

settings = get_settings()


class LeadQualificationAgent:
    """
    AI-powered lead qualification using Claude.

    Automatically scores and qualifies leads based on:
    - Demographics and firmographics
    - Engagement history
    - Budget indicators
    - Communication patterns
    - Trading experience level
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize lead qualification agent.

        Args:
            api_key: Anthropic API key
        """
        self.api_key = api_key or settings.anthropic_api_key

        if not self.api_key:
            logger.warning("Anthropic API key not configured")
            self.client = None
            return

        try:
            self.client = Anthropic(api_key=self.api_key)
            logger.info("Lead qualification agent initialized")
        except Exception as e:
            logger.error(f"Lead qualification agent error: {e}")
            self.client = None

    def qualify_lead(self, lead_data: Dict) -> Dict:
        """
        Qualify and score a lead using AI analysis.

        Args:
            lead_data: Lead information dictionary
                - email: Email address
                - name: Full name
                - source: Lead source (website, referral, ad)
                - message: Initial message/inquiry
                - interests: List of interests
                - metadata: Additional data

        Returns:
            Qualification results with score and recommendations

        Example:
            >>> agent = LeadQualificationAgent()
            >>> result = agent.qualify_lead({
            ...     "email": "trader@example.com",
            ...     "name": "John Smith",
            ...     "source": "website",
            ...     "message": "Looking for pro trading signals",
            ...     "interests": ["forex", "automation"]
            ... })
            >>> print(result['score'], result['tier'])
        """
        if not self.client:
            logger.warning("Claude client not available - using fallback")
            return self._fallback_qualification(lead_data)

        try:
            # Prepare prompt for Claude
            prompt = self._build_qualification_prompt(lead_data)

            # Call Claude API
            message = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            response_text = message.content[0].text
            qualification = self._parse_qualification_response(response_text)

            # Add lead data
            qualification.update({
                "email": lead_data.get("email"),
                "name": lead_data.get("name"),
                "source": lead_data.get("source"),
                "qualified_at": datetime.utcnow().isoformat(),
            })

            logger.info(
                f"Lead qualified: {lead_data.get('email')} - Score: {qualification.get('score')}/100",
                extra=qualification
            )

            return qualification

        except Exception as e:
            logger.error(f"Lead qualification error: {e}")
            return self._fallback_qualification(lead_data)

    def _build_qualification_prompt(self, lead_data: Dict) -> str:
        """Build qualification prompt for Claude."""
        return f"""You are a lead qualification specialist for a quantum trading AI platform targeting the South African market.

Analyze this lead and provide a qualification score and recommendations.

LEAD INFORMATION:
- Name: {lead_data.get('name', 'Unknown')}
- Email: {lead_data.get('email')}
- Source: {lead_data.get('source', 'Unknown')}
- Initial Message: {lead_data.get('message', 'No message')}
- Interests: {', '.join(lead_data.get('interests', []))}
- Additional Data: {lead_data.get('metadata', {})}

QUALIFICATION CRITERIA:
1. Budget Potential (0-25 points)
   - Keywords indicating financial capacity
   - Business vs personal email domain
   - Professional title/role

2. Trading Experience (0-25 points)
   - Mentions of trading platforms (MT5, etc.)
   - Technical knowledge level
   - Past trading experience

3. Urgency & Intent (0-25 points)
   - Action words (want, need, looking for)
   - Timeline indicators
   - Specific requirements

4. Fit with Product (0-25 points)
   - Alignment with our offerings
   - South African market relevance
   - Technology readiness

OUTPUT FORMAT (JSON):
{{
  "score": <0-100>,
  "tier": "<hot|warm|cold>",
  "recommended_plan": "<basic|pro|premium|bot|enterprise>",
  "reasoning": "<brief explanation>",
  "next_actions": ["<action 1>", "<action 2>"],
  "red_flags": ["<flag 1>", "<flag 2>"] or [],
  "estimated_ltv": <amount in ZAR>
}}

Provide only the JSON output, no additional text."""

    def _parse_qualification_response(self, response: str) -> Dict:
        """Parse Claude's qualification response."""
        import json

        try:
            # Extract JSON from response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)

            # Fallback parsing if JSON not found
            logger.warning("Could not parse JSON from Claude response")
            return self._fallback_qualification({})

        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return self._fallback_qualification({})

    def _fallback_qualification(self, lead_data: Dict) -> Dict:
        """Fallback qualification when Claude is unavailable."""
        # Simple rule-based scoring
        score = 50  # Base score

        # Check email domain
        email = lead_data.get('email', '')
        if any(domain in email for domain in ['gmail', 'yahoo', 'hotmail']):
            score -= 10  # Personal email
        else:
            score += 10  # Business email

        # Check message for keywords
        message = lead_data.get('message', '').lower()
        if any(word in message for word in ['urgent', 'immediately', 'asap']):
            score += 15  # High urgency

        if any(word in message for word in ['enterprise', 'company', 'business']):
            score += 10  # Business prospect

        # Determine tier
        if score >= 70:
            tier = "hot"
            plan = "premium"
        elif score >= 50:
            tier = "warm"
            plan = "pro"
        else:
            tier = "cold"
            plan = "basic"

        return {
            "score": min(100, max(0, score)),
            "tier": tier,
            "recommended_plan": plan,
            "reasoning": "Automated rule-based qualification (Claude unavailable)",
            "next_actions": ["Send welcome email", "Schedule follow-up"],
            "red_flags": [],
            "estimated_ltv": score * 50,  # Simple LTV estimate
        }

    def batch_qualify_leads(self, leads: List[Dict]) -> List[Dict]:
        """
        Qualify multiple leads in batch.

        Args:
            leads: List of lead data dictionaries

        Returns:
            List of qualification results
        """
        results = []

        for lead in leads:
            try:
                result = self.qualify_lead(lead)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch qualification error for {lead.get('email')}: {e}")

        logger.info(f"Batch qualified {len(results)}/{len(leads)} leads")
        return results

    def update_lead_score(
        self,
        email: str,
        interaction_type: str,
        details: Dict
    ) -> Optional[Dict]:
        """
        Update lead score based on new interaction.

        Args:
            email: Lead email
            interaction_type: Type of interaction (email_open, link_click, form_submit, etc.)
            details: Interaction details

        Returns:
            Updated qualification
        """
        try:
            # Score adjustments based on interaction
            score_changes = {
                "email_open": +5,
                "link_click": +10,
                "form_submit": +15,
                "demo_request": +20,
                "pricing_view": +15,
                "trial_start": +25,
                "subscription": +50,
            }

            adjustment = score_changes.get(interaction_type, 0)

            logger.info(
                f"Lead score updated: {email} - {interaction_type} ({adjustment:+d})",
                extra={"email": email, "interaction": interaction_type, "adjustment": adjustment}
            )

            return {
                "email": email,
                "score_adjustment": adjustment,
                "interaction_type": interaction_type,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Lead score update error: {e}")
            return None

    def get_lead_recommendations(self, lead_score: int, tier: str) -> List[str]:
        """
        Get next action recommendations for a lead.

        Args:
            lead_score: Lead qualification score
            tier: Lead tier (hot, warm, cold)

        Returns:
            List of recommended actions
        """
        if tier == "hot" or lead_score >= 80:
            return [
                "Immediate personal outreach",
                "Offer premium plan trial",
                "Schedule 1-on-1 demo call",
                "Provide custom pricing",
                "Fast-track onboarding",
            ]
        elif tier == "warm" or lead_score >= 60:
            return [
                "Send personalized email",
                "Offer pro plan trial",
                "Share case studies",
                "Schedule follow-up in 2 days",
                "Add to nurture campaign",
            ]
        else:  # cold
            return [
                "Add to newsletter",
                "Send educational content",
                "Offer basic plan trial",
                "Follow up in 7 days",
                "Monitor engagement",
            ]
