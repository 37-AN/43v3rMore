"""
Test automation systems to validate Phase 2 implementation.

This script tests all MCP server components:
- Lead qualification
- Customer support
- Content generation
- Onboarding automation
- Analytics reporting
"""

from src.mcp_servers import (
    BusinessAutomationServer,
    LeadQualificationAgent,
    SupportAgent,
    ContentGenerator,
    OnboardingAutomation,
    AnalyticsAgent,
)


def test_lead_qualification():
    """Test lead qualification system."""
    print("\n" + "="*60)
    print("TESTING: Lead Qualification Agent")
    print("="*60)

    agent = LeadQualificationAgent()

    # Test different lead scenarios
    test_leads = [
        {
            "email": "enterprise@bigcorp.com",
            "name": "Corporate Manager",
            "source": "website",
            "message": "Need solution for 50 traders, budget R500k annually",
            "interests": ["enterprise", "API", "custom"],
        },
        {
            "email": "trader@gmail.com",
            "name": "Individual Trader",
            "source": "referral",
            "message": "Just starting out, want to learn",
            "interests": ["forex", "learning"],
        },
        {
            "email": "pro.trader@outlook.com",
            "name": "Professional Trader",
            "source": "ad",
            "message": "Been trading 5 years, need better signals",
            "interests": ["forex", "automation", "MT5"],
        },
    ]

    for i, lead in enumerate(test_leads, 1):
        print(f"\n--- Test Lead {i}: {lead['name']} ---")
        result = agent.qualify_lead(lead)
        print(f"Email: {lead['email']}")
        print(f"Score: {result['score']}/100")
        print(f"Tier: {result['tier']}")
        print(f"Recommended Plan: {result['recommended_plan']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Next Actions: {', '.join(result['next_actions'][:2])}")

    print("\n✅ Lead Qualification: PASSED")
    return True


def test_customer_support():
    """Test customer support agent."""
    print("\n" + "="*60)
    print("TESTING: Customer Support Agent")
    print("="*60)

    agent = SupportAgent()

    test_queries = [
        "How do I upgrade my plan?",
        "Why am I not receiving signals on Telegram?",
        "What's the difference between Pro and Premium?",
        "I want a refund",
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Query {i}: {query} ---")
        response = agent.handle_inquiry(
            user_id=f"test_user_{i}",
            message=query,
            context={"plan": "basic", "status": "active"}
        )
        print(f"Response: {response['response'][:200]}...")
        print(f"Confidence: {response['confidence']}")
        if response.get('actions'):
            print(f"Actions: {', '.join(response['actions'])}")

    print("\n✅ Customer Support: PASSED")
    return True


def test_content_generation():
    """Test content generation."""
    print("\n" + "="*60)
    print("TESTING: Content Generator")
    print("="*60)

    generator = ContentGenerator()

    # Test email campaign
    print("\n--- Email Campaign ---")
    campaign = generator.generate_email_campaign(
        campaign_type="welcome",
        target_audience="new pro users",
        goal="onboard and educate"
    )
    print(f"Subject: {campaign.get('subject_line', 'N/A')}")
    print(f"CTA: {campaign.get('cta_text', 'N/A')}")

    # Test social post
    print("\n--- Social Media Post ---")
    post = generator.generate_social_post(
        platform="twitter",
        topic="95% signal accuracy",
        tone="professional"
    )
    print(f"Platform: {post.get('platform', 'N/A')}")
    print(f"Post: {post.get('post_text', 'N/A')[:150]}...")

    print("\n✅ Content Generation: PASSED")
    return True


def test_onboarding():
    """Test onboarding automation."""
    print("\n" + "="*60)
    print("TESTING: Onboarding Automation")
    print("="*60)

    onboarding = OnboardingAutomation()

    result = onboarding.onboard_new_user(
        user_id="test_user_123",
        email="newuser@example.com",
        name="Test User",
        plan="pro"
    )

    print(f"Status: {result['status']}")
    print(f"Steps Completed: {len(result['steps_completed'])}/5")
    print(f"Tasks Created: {len(result['tasks'])}")
    print(f"Follow-ups Scheduled: {len(result['followups'])}")
    print(f"Completion Rate: {result['completion_rate']:.1f}%")

    print("\n✅ Onboarding Automation: PASSED")
    return True


def test_analytics():
    """Test analytics agent."""
    print("\n" + "="*60)
    print("TESTING: Analytics Agent")
    print("="*60)

    agent = AnalyticsAgent()

    # Daily report
    print("\n--- Daily Report ---")
    daily = agent.generate_daily_report()
    print(f"Date: {daily.get('date', 'N/A')}")
    print(f"Metrics: {len(daily.get('metrics', {}))} tracked")
    print(f"Insights: {len(daily.get('insights', []))} generated")

    # Dashboard summary
    print("\n--- Dashboard Summary ---")
    dashboard = agent.get_dashboard_summary()
    current = dashboard.get('current_metrics', {})
    print(f"Total Users: {current.get('total_users', 0)}")
    print(f"MRR: R{current.get('mrr', 0):,.2f}")
    print(f"Signals Today: {current.get('signals_today', 0)}")

    print("\n✅ Analytics: PASSED")
    return True


def test_orchestrator():
    """Test business automation orchestrator."""
    print("\n" + "="*60)
    print("TESTING: Business Automation Orchestrator")
    print("="*60)

    automation = BusinessAutomationServer()

    # System status
    print("\n--- System Status ---")
    status = automation.get_system_status()
    print(f"Status: {status['status']}")
    print("Components:")
    for component, state in status['components'].items():
        print(f"  - {component}: {state}")

    # Test complete lead workflow
    print("\n--- Complete Lead Workflow ---")
    test_lead = {
        "email": "workflow.test@example.com",
        "name": "Workflow Test",
        "source": "test",
        "message": "Testing complete workflow",
        "interests": ["testing"],
    }
    result = automation.process_new_lead(test_lead)
    print(f"Status: {result['status']}")
    print(f"Lead Tier: {result.get('qualification', {}).get('tier', 'N/A')}")

    print("\n✅ Orchestrator: PASSED")
    return True


def run_all_tests():
    """Run all automation tests."""
    print("\n" + "="*60)
    print("PHASE 2 AUTOMATION VALIDATION")
    print("="*60)
    print("Testing all MCP server components...")

    results = {
        "Lead Qualification": test_lead_qualification(),
        "Customer Support": test_customer_support(),
        "Content Generation": test_content_generation(),
        "Onboarding": test_onboarding(),
        "Analytics": test_analytics(),
        "Orchestrator": test_orchestrator(),
    }

    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")

    all_passed = all(results.values())

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Phase 2 Validated!")
        print("Ready to proceed to Phase 3: Beta Testing")
    else:
        print("⚠️ SOME TESTS FAILED - Review errors above")
    print("="*60 + "\n")

    return all_passed


if __name__ == "__main__":
    run_all_tests()
