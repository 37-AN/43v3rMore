"""Marketing content generation using Claude AI."""

from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
from loguru import logger

from ..utils.config import get_settings

settings = get_settings()


class ContentGenerator:
    """
    AI-powered content generation for marketing automation.

    Generates:
    - Email campaigns
    - Social media posts
    - Blog articles
    - Landing page copy
    - Ad copy
    - Video scripts
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize content generator."""
        self.api_key = api_key or settings.anthropic_api_key

        if not self.api_key:
            logger.warning("Anthropic API key not configured")
            self.client = None
            return

        try:
            self.client = Anthropic(api_key=self.api_key)
            logger.info("Content generator initialized")
        except Exception as e:
            logger.error(f"Content generator error: {e}")
            self.client = None

    def generate_email_campaign(
        self,
        campaign_type: str,
        target_audience: str,
        goal: str
    ) -> Dict:
        """
        Generate email campaign content.

        Args:
            campaign_type: Type of campaign (welcome, nurture, promotion, etc.)
            target_audience: Target audience description
            goal: Campaign goal

        Returns:
            Email campaign with subject and body

        Example:
            >>> generator = ContentGenerator()
            >>> campaign = generator.generate_email_campaign(
            ...     campaign_type="welcome",
            ...     target_audience="new basic plan subscribers",
            ...     goal="onboard and educate about signals"
            ... )
        """
        if not self.client:
            return self._fallback_email(campaign_type)

        try:
            prompt = f"""Create a professional email campaign for Quantum Trading AI, a South African quantum computing-powered trading signal service.

CAMPAIGN DETAILS:
- Type: {campaign_type}
- Target Audience: {target_audience}
- Goal: {goal}

COMPANY CONTEXT:
- Service: AI trading signals using quantum phase estimation
- Target Market: South African retail traders
- USP: 95%+ signal accuracy using quantum computing
- Plans: R500-R10K/month
- Channels: Telegram, WhatsApp, Email

TONE & STYLE:
- Professional yet approachable
- Data-driven and credible
- Action-oriented
- South African context (use Rand, local references)

OUTPUT FORMAT (JSON):
{{
  "subject_line": "<compelling subject 40-60 chars>",
  "preview_text": "<preview text 80-100 chars>",
  "body_html": "<complete HTML email body>",
  "body_text": "<plain text version>",
  "cta_text": "<call-to-action button text>",
  "cta_url": "<call-to-action URL>",
  "personalization_tags": ["<tag1>", "<tag2>"]
}}

Include:
- Attention-grabbing subject line
- Personalized greeting
- Clear value proposition
- Social proof or statistics
- Strong call-to-action
- Professional signature

Output only the JSON."""

            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result_text = response.content[0].text
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1

            if json_start >= 0:
                campaign = json.loads(result_text[json_start:json_end])
                campaign['generated_at'] = datetime.utcnow().isoformat()
                campaign['campaign_type'] = campaign_type

                logger.info(f"Email campaign generated: {campaign_type}")
                return campaign

            return self._fallback_email(campaign_type)

        except Exception as e:
            logger.error(f"Email generation error: {e}")
            return self._fallback_email(campaign_type)

    def generate_social_post(
        self,
        platform: str,
        topic: str,
        tone: str = "professional"
    ) -> Dict:
        """
        Generate social media post.

        Args:
            platform: Platform (twitter, linkedin, facebook, instagram)
            topic: Post topic
            tone: Desired tone

        Returns:
            Social media post content
        """
        if not self.client:
            return self._fallback_social(platform, topic)

        try:
            char_limits = {
                "twitter": 280,
                "linkedin": 3000,
                "facebook": 500,
                "instagram": 2200,
            }

            limit = char_limits.get(platform, 500)

            prompt = f"""Create a {platform} post for Quantum Trading AI.

Topic: {topic}
Tone: {tone}
Character Limit: {limit}

Company: Quantum Trading AI - South African quantum computing trading signals
USP: 95%+ accuracy, R500-R10K/month plans

Requirements:
- Engaging hook in first line
- Include relevant hashtags
- Call-to-action
- Professional yet engaging
- South African context

Output JSON:
{{
  "post_text": "<complete post>",
  "hashtags": ["<hashtag1>", "<hashtag2>"],
  "media_suggestions": ["<suggestion1>"],
  "best_time_to_post": "<time recommendation>",
  "engagement_prediction": "<high|medium|low>"
}}

Output only JSON."""

            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result_text = response.content[0].text
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1

            if json_start >= 0:
                post = json.loads(result_text[json_start:json_end])
                post['platform'] = platform
                post['generated_at'] = datetime.utcnow().isoformat()

                logger.info(f"Social post generated: {platform} - {topic}")
                return post

            return self._fallback_social(platform, topic)

        except Exception as e:
            logger.error(f"Social post generation error: {e}")
            return self._fallback_social(platform, topic)

    def generate_blog_article(
        self,
        title: str,
        keywords: List[str],
        target_length: int = 1500
    ) -> Dict:
        """
        Generate blog article.

        Args:
            title: Article title
            keywords: SEO keywords
            target_length: Target word count

        Returns:
            Complete blog article
        """
        if not self.client:
            return {"title": title, "content": "Content generation unavailable", "seo_optimized": False}

        try:
            prompt = f"""Write a comprehensive blog article for Quantum Trading AI's website.

Title: {title}
Keywords: {', '.join(keywords)}
Target Length: {target_length} words

Company Context:
- Quantum Trading AI: South African quantum computing trading signals
- Target Audience: Retail traders, tech-savvy investors
- USP: 95%+ accuracy using quantum phase estimation

Article Requirements:
- SEO-optimized (include keywords naturally)
- Clear structure with H2/H3 headings
- Engaging introduction
- Data-driven content
- Actionable insights
- Strong conclusion with CTA
- Professional, authoritative tone

Output JSON:
{{
  "title": "<SEO-optimized title>",
  "meta_description": "<150-160 chars>",
  "introduction": "<opening paragraphs>",
  "sections": [
    {{
      "heading": "<H2 heading>",
      "content": "<section content>"
    }}
  ],
  "conclusion": "<closing paragraphs>",
  "cta": "<call-to-action>",
  "word_count": <actual count>,
  "reading_time": "<X minutes>"
}}

Write comprehensive, valuable content."""

            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result_text = response.content[0].text
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1

            if json_start >= 0:
                article = json.loads(result_text[json_start:json_end])
                article['keywords'] = keywords
                article['generated_at'] = datetime.utcnow().isoformat()

                logger.info(f"Blog article generated: {title}")
                return article

            return {"title": title, "content": "Generation failed", "seo_optimized": False}

        except Exception as e:
            logger.error(f"Blog generation error: {e}")
            return {"title": title, "content": f"Error: {e}", "seo_optimized": False}

    def generate_landing_page_copy(
        self,
        page_goal: str,
        target_audience: str
    ) -> Dict:
        """
        Generate landing page copy.

        Args:
            page_goal: Landing page goal
            target_audience: Target audience

        Returns:
            Complete landing page copy
        """
        if not self.client:
            return self._fallback_landing_page()

        try:
            prompt = f"""Create high-converting landing page copy for Quantum Trading AI.

Page Goal: {page_goal}
Target Audience: {target_audience}

Company: Quantum Trading AI - 95%+ accurate trading signals using quantum computing
Market: South Africa (ZAR pricing)

Landing Page Structure:
1. Hero Section (headline, subheadline, CTA)
2. Social Proof (stats, testimonials)
3. Features/Benefits
4. How It Works
5. Pricing
6. FAQ
7. Final CTA

Output JSON with each section's copy.

Focus on:
- Clear value proposition
- Specific benefits (not features)
- Urgency and scarcity
- Trust signals
- Multiple CTAs
- Mobile-friendly

Make it conversion-optimized and persuasive."""

            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response (simplified for brevity)
            result_text = response.content[0].text

            logger.info(f"Landing page copy generated: {page_goal}")
            return {
                "copy": result_text,
                "page_goal": page_goal,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Landing page generation error: {e}")
            return self._fallback_landing_page()

    def _fallback_email(self, campaign_type: str) -> Dict:
        """Fallback email when Claude unavailable."""
        return {
            "subject_line": "Welcome to Quantum Trading AI",
            "preview_text": "Start receiving high-accuracy trading signals today",
            "body_html": "<h1>Welcome!</h1><p>Thank you for subscribing to Quantum Trading AI.</p>",
            "body_text": "Welcome! Thank you for subscribing to Quantum Trading AI.",
            "cta_text": "Get Started",
            "cta_url": "https://quantumtrading.ai/dashboard",
            "campaign_type": campaign_type,
        }

    def _fallback_social(self, platform: str, topic: str) -> Dict:
        """Fallback social post."""
        return {
            "post_text": f"Quantum Trading AI: 95%+ accurate signals using quantum computing. {topic}",
            "hashtags": ["#trading", "#forex", "#AI", "#quantumcomputing"],
            "platform": platform,
        }

    def _fallback_landing_page(self) -> Dict:
        """Fallback landing page copy."""
        return {
            "copy": "Quantum Trading AI - Get 95%+ accurate trading signals",
            "generated_at": datetime.utcnow().isoformat(),
        }
