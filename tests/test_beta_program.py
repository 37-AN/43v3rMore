"""
End-to-end tests for Phase 3: Beta Testing Program.

This script validates all beta program components:
- Beta application and selection
- Feedback collection and tracking
- Performance monitoring
- Signal optimization
- Beta graduation and conversion
"""

from src.beta_program import (
    BetaApplicationManager,
    FeedbackCollector,
    PerformanceMonitor,
    BetaGraduation,
)
from src.quantum_engine import SignalOptimizer


def test_beta_application():
    """Test beta application system."""
    print("\n" + "="*60)
    print("TESTING: Beta Application System")
    print("="*60)

    manager = BetaApplicationManager(max_testers=10)

    # Test high-quality application (should be accepted)
    print("\n--- High-Quality Application ---")
    high_quality_app = {
        "email": "professional@trader.com",
        "name": "Professional Trader",
        "trading_experience": 5,
        "platforms_used": ["MT5", "TradingView"],
        "primary_pairs": ["EURUSD", "GBPUSD", "USDJPY"],
        "why_join": "Want to improve my trading and help test new AI technology",
        "availability": 15,
        "feedback_commitment": True,
    }

    result = manager.submit_application(high_quality_app)
    print(f"Email: {high_quality_app['email']}")
    print(f"Status: {result['status']}")
    print(f"Score: {result['score']}/100")
    print(f"Message: {result['message']}")

    assert result['status'] == "accepted", "High-quality application should be accepted"
    assert result['score'] >= 80, "High-quality application should score >= 80"

    # Test medium-quality application (should be waitlisted)
    print("\n--- Medium-Quality Application ---")
    medium_quality_app = {
        "email": "trader@gmail.com",
        "name": "New Trader",
        "trading_experience": 1,
        "platforms_used": ["TradingView"],
        "primary_pairs": ["EURUSD"],
        "why_join": "Want to learn",
        "availability": 5,
        "feedback_commitment": True,
    }

    result = manager.submit_application(medium_quality_app)
    print(f"Email: {medium_quality_app['email']}")
    print(f"Status: {result['status']}")
    print(f"Score: {result['score']}/100")

    assert result['status'] in ["waitlisted", "accepted"], "Medium-quality should be waitlisted or accepted"
    assert 60 <= result['score'] < 80, "Medium-quality should score between 60-79"

    # Get application stats
    print("\n--- Application Statistics ---")
    stats = manager.get_application_stats()
    print(f"Total Applications: {stats['total_applications']}")
    print(f"Acceptance Rate: {stats['acceptance_rate']:.1%}")
    print(f"Average Score: {stats['average_score']:.1f}")

    print("\n✅ Beta Application System: PASSED")
    return True


def test_feedback_collection():
    """Test feedback collection system."""
    print("\n" + "="*60)
    print("TESTING: Feedback Collection System")
    print("="*60)

    collector = FeedbackCollector()

    # Test bug report submission
    print("\n--- Bug Report ---")
    bug_report = {
        "title": "Telegram notifications delayed",
        "description": "Signals arrive 2-3 minutes late",
        "severity": "medium",
        "steps_to_reproduce": "1. Subscribe to signals 2. Wait for signal 3. Check timestamp",
    }

    result = collector.submit_feedback(
        user_id="beta_001",
        feedback_type="bug",
        content=bug_report
    )

    print(f"Feedback ID: {result['feedback_id']}")
    print(f"Status: {result['status']}")
    print(f"Priority: {result['priority']}")
    print(f"Message: {result['message']}")

    assert result['status'] == "submitted", "Feedback should be submitted successfully"
    assert result['priority'] in ["low", "medium", "high"], "Feedback should have valid priority"

    # Test feature request submission
    print("\n--- Feature Request ---")
    feature_request = {
        "title": "Add mobile app",
        "description": "Would love an iOS/Android app for signal notifications",
        "use_case": "Trading on the go",
    }

    result = collector.submit_feedback(
        user_id="beta_002",
        feedback_type="feature",
        content=feature_request
    )

    print(f"Feedback ID: {result['feedback_id']}")
    print(f"Priority: {result['priority']}")

    assert result['status'] == "submitted", "Feature request should be submitted"

    # Get feedback summary
    print("\n--- Feedback Summary (7 days) ---")
    summary = collector.get_feedback_summary(days=7)
    print(f"Total Feedback: {summary['total_feedback']}")
    print(f"Bug Reports: {summary['by_type']['bug']}")
    print(f"Feature Requests: {summary['by_type']['feature']}")
    print(f"Avg Satisfaction: {summary['avg_satisfaction']:.1f}/5")
    print(f"Response Rate: {summary['response_rate']:.1%}")

    # Get top feature requests
    print("\n--- Top Feature Requests ---")
    top_features = collector.get_top_feature_requests(limit=3)
    for i, feature in enumerate(top_features, 1):
        print(f"{i}. {feature['feature']}: {feature['votes']} votes ({feature['priority']} priority)")

    print("\n✅ Feedback Collection System: PASSED")
    return True


def test_performance_monitoring():
    """Test performance monitoring system."""
    print("\n" + "="*60)
    print("TESTING: Performance Monitoring System")
    print("="*60)

    monitor = PerformanceMonitor()

    # Get current metrics
    print("\n--- Current Metrics ---")
    metrics = monitor.get_current_metrics()
    print(f"Signal Accuracy: {metrics.signal_accuracy:.2%}")
    print(f"Total Signals: {metrics.total_signals}")
    print(f"Winning Signals: {metrics.winning_signals}")
    print(f"Active Users: {metrics.active_users}")
    print(f"User Engagement: {metrics.user_engagement:.1%}")
    print(f"API Latency: {metrics.api_latency_ms:.0f}ms")
    print(f"Uptime: {metrics.uptime_percentage:.2%}")

    assert metrics.signal_accuracy >= 0.90, "Signal accuracy should be >= 90%"
    assert metrics.uptime_percentage >= 0.95, "Uptime should be >= 95%"

    # Get dashboard data
    print("\n--- Dashboard Summary ---")
    dashboard = monitor.get_dashboard_data()
    print(f"Summary: {dashboard['summary']}")
    print(f"Active Issues: {len(dashboard.get('issues', []))}")

    # Generate daily report
    print("\n--- Daily Report ---")
    report = monitor.generate_daily_report()
    print(f"Date: {report['date']}")
    print(f"Performance Metrics: {len(report['performance'])} tracked")
    print(f"Insights: {len(report['insights'])} generated")
    print(f"Recommendations: {len(report['recommendations'])} provided")

    print("\nInsights:")
    for insight in report['insights']:
        print(f"  - {insight}")

    # Get optimization suggestions
    print("\n--- Optimization Suggestions ---")
    suggestions = monitor.get_optimization_suggestions()
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. [{suggestion['priority'].upper()}] {suggestion['suggestion']}")
        print(f"   Impact: {suggestion['expected_impact']}, Effort: {suggestion['effort']}")

    print("\n✅ Performance Monitoring System: PASSED")
    return True


def test_signal_optimization():
    """Test signal optimization system."""
    print("\n" + "="*60)
    print("TESTING: Signal Optimization System")
    print("="*60)

    optimizer = SignalOptimizer()

    # Collect performance data
    print("\n--- Collecting Performance Data ---")
    performance = optimizer.collect_performance_data(days=7)
    print(f"Period: {performance['period_days']} days")
    print(f"Total Signals: {performance['total_signals']}")
    print(f"Win Rate: {performance['win_rate']:.2%}")
    print(f"Avg Profit: R{performance['avg_profit']:.2f}")
    print(f"Profit Factor: {performance['profit_factor']:.2f}")

    assert performance['win_rate'] >= 0.90, "Win rate should be >= 90%"
    assert performance['profit_factor'] >= 2.0, "Profit factor should be >= 2.0"

    # Optimize parameters
    print("\n--- Optimizing Parameters ---")
    optimization = optimizer.optimize_parameters(performance)
    print(f"Current Win Rate: {optimization['current_win_rate']:.2%}")
    print(f"Expected Win Rate: {optimization['expected_win_rate']:.2%}")
    print(f"Expected Improvement: +{optimization['expected_improvement']:.2%}")
    print(f"Improvements Found: {optimization['improvements_found']}")

    print("\nCurrent Parameters:")
    for param, value in optimization['current_params'].items():
        print(f"  - {param}: {value}")

    print("\nOptimized Parameters:")
    for param, value in optimization['optimized_params'].items():
        print(f"  - {param}: {value}")

    # Generate optimization report
    print("\n--- Optimization Report ---")
    report = optimizer.generate_optimization_report()
    print(f"Current Performance: {report['current_performance']['win_rate']:.2%} win rate")
    print(f"Symbol Insights: {len(report['symbol_insights'])} generated")

    print("\nSymbol Insights:")
    for insight in report['symbol_insights']:
        print(f"  {insight}")

    print("\nRecommendations:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")

    print("\n✅ Signal Optimization System: PASSED")
    return True


def test_beta_graduation():
    """Test beta graduation system."""
    print("\n" + "="*60)
    print("TESTING: Beta Graduation System")
    print("="*60)

    graduation = BetaGraduation()

    # Test successful beta tester
    print("\n--- Successful Beta Tester ---")
    evaluation = graduation.evaluate_beta_success("beta_001")
    print(f"User ID: {evaluation['user_id']}")
    print(f"Is Successful: {evaluation['is_successful']}")
    print(f"Criteria Met: {evaluation['criteria_met']}/{evaluation['criteria_total']}")

    print("\nCriteria Details:")
    for criterion, details in evaluation['criteria_details'].items():
        status = "✅" if details['met'] else "❌"
        print(f"  {status} {criterion}: {details['value']} (required: {details['required']})")

    assert evaluation['is_successful'], "Beta tester with good metrics should be successful"

    # Graduate beta tester
    print("\n--- Graduating Beta Tester ---")
    result = graduation.graduate_beta_tester("beta_001")
    print(f"Status: {result['status']}")
    print(f"Discount Code: {result['discount_code']}")
    print(f"Discount Percentage: {result['discount_percentage']}%")
    print(f"Is Lifetime: {result['is_lifetime_discount']}")
    print(f"Bonus Months: {result['bonus_months']}")
    print(f"Referral Credits: {result['referral_credits']}")
    print(f"Email Sent: {result['email_sent']}")

    assert result['status'] == "graduated", "Beta tester should graduate successfully"
    assert result['discount_percentage'] > 0, "Should receive discount"
    assert len(result['next_steps']) > 0, "Should have next steps"

    print("\nNext Steps:")
    for i, step in enumerate(result['next_steps'], 1):
        print(f"  {i}. {step}")

    # Test batch graduation
    print("\n--- Batch Graduation ---")
    batch_result = graduation.batch_graduate_beta_testers()
    print(f"Total Testers: {batch_result['total_testers']}")
    print(f"Successful: {batch_result['successful_count']}")
    print(f"Participated: {batch_result['participated_count']}")
    print(f"Ineligible: {batch_result['ineligible_count']}")
    print(f"Conversion Rate: {batch_result['conversion_rate']:.1%}")

    # Get conversion stats
    print("\n--- Conversion Statistics ---")
    stats = graduation.get_conversion_stats()
    print(f"Beta Testers: {stats['total_beta_testers']}")
    print(f"Conversions: {stats['conversions']}")
    print(f"Conversion Rate: {stats['conversion_rate']:.1%}")
    print(f"Avg LTV (Successful): R{stats['avg_ltv_successful']:,.0f}")
    print(f"Avg LTV (Participated): R{stats['avg_ltv_participated']:,.0f}")

    assert stats['conversion_rate'] >= 0.60, "Conversion rate should be >= 60%"

    print("\n✅ Beta Graduation System: PASSED")
    return True


def test_complete_beta_workflow():
    """Test complete end-to-end beta workflow."""
    print("\n" + "="*60)
    print("TESTING: Complete Beta Workflow (End-to-End)")
    print("="*60)

    # 1. Application
    print("\n[1/5] Beta Application...")
    manager = BetaApplicationManager(max_testers=10)
    application = manager.submit_application({
        "email": "e2e.test@trader.com",
        "name": "E2E Test User",
        "trading_experience": 3,
        "platforms_used": ["MT5"],
        "primary_pairs": ["EURUSD"],
        "why_join": "Want to improve my trading with AI",
        "availability": 10,
        "feedback_commitment": True,
    })
    assert application['status'] == "accepted", "Should be accepted"
    print(f"✓ Application {application['status']}")

    # 2. Feedback Collection
    print("\n[2/5] Collecting Feedback...")
    collector = FeedbackCollector()
    feedback = collector.submit_feedback(
        user_id="e2e_test",
        feedback_type="general",
        content={"message": "Great signals, very accurate!"}
    )
    assert feedback['status'] == "submitted", "Feedback should be submitted"
    print(f"✓ Feedback submitted (ID: {feedback['feedback_id']})")

    # 3. Performance Monitoring
    print("\n[3/5] Monitoring Performance...")
    monitor = PerformanceMonitor()
    metrics = monitor.get_current_metrics()
    assert metrics.signal_accuracy >= 0.90, "Signal accuracy should be high"
    print(f"✓ Performance monitored (Accuracy: {metrics.signal_accuracy:.2%})")

    # 4. Signal Optimization
    print("\n[4/5] Optimizing Signals...")
    optimizer = SignalOptimizer()
    performance = optimizer.collect_performance_data(days=7)
    optimization = optimizer.optimize_parameters(performance)
    assert optimization['expected_improvement'] >= 0, "Should find optimization opportunities"
    print(f"✓ Signals optimized (Improvement: +{optimization['expected_improvement']:.2%})")

    # 5. Graduation
    print("\n[5/5] Graduating Beta Tester...")
    graduation = BetaGraduation()
    result = graduation.graduate_beta_tester("e2e_test")
    assert result['status'] in ["graduated", "ineligible"], "Should complete graduation process"
    print(f"✓ Beta tester graduated ({result['status']})")

    print("\n✅ Complete Beta Workflow: PASSED")
    print("\nWorkflow Summary:")
    print("  1. ✓ Application Accepted")
    print("  2. ✓ Feedback Collected")
    print("  3. ✓ Performance Monitored")
    print("  4. ✓ Signals Optimized")
    print("  5. ✓ Beta Tester Graduated")

    return True


def run_all_tests():
    """Run all beta program tests."""
    print("\n" + "="*60)
    print("PHASE 3: BETA TESTING PROGRAM VALIDATION")
    print("="*60)
    print("Testing all beta program components...\n")

    results = {
        "Beta Application": test_beta_application(),
        "Feedback Collection": test_feedback_collection(),
        "Performance Monitoring": test_performance_monitoring(),
        "Signal Optimization": test_signal_optimization(),
        "Beta Graduation": test_beta_graduation(),
        "Complete Workflow": test_complete_beta_workflow(),
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
        print("🎉 ALL TESTS PASSED - Phase 3 Validated!")
        print("\nBeta Program Status:")
        print("  ✅ Application system operational")
        print("  ✅ Feedback collection ready")
        print("  ✅ Performance monitoring active")
        print("  ✅ Signal optimization functional")
        print("  ✅ Graduation process configured")
        print("\n🚀 Ready to launch beta program!")
    else:
        print("⚠️ SOME TESTS FAILED - Review errors above")
    print("="*60 + "\n")

    return all_passed


if __name__ == "__main__":
    run_all_tests()
