"""MCP servers for business automation using Claude AI."""

from .business_automation import BusinessAutomationServer
from .lead_manager import LeadQualificationAgent
from .support_agent import SupportAgent
from .content_generator import ContentGenerator
from .onboarding import OnboardingAutomation
from .analytics import AnalyticsAgent

__all__ = [
    "BusinessAutomationServer",
    "LeadQualificationAgent",
    "SupportAgent",
    "ContentGenerator",
    "OnboardingAutomation",
    "AnalyticsAgent",
]

__version__ = "2.0.0"  # Phase 2 - Business Automation
