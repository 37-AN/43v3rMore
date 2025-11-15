"""Business analytics and reporting using Claude AI."""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from anthropic import Anthropic
from loguru import logger

from ..utils.config import get_settings
from ..database.queries import UserQueries, SignalQueries, AnalyticsQueries

settings = get_settings()


class AnalyticsAgent:
    """
    AI-powered business analytics and insights.

    Provides:
    - Automated reporting
    - Trend analysis
    - Performance insights
    - Growth recommendations
    - Churn prediction
    - Revenue forecasting
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize analytics agent."""
        self.api_key = api_key or settings.anthropic_api_key

        if not self.api_key:
            logger.warning("Anthropic API key not configured")
            self.client = None
        else:
            self.client = Anthropic(api_key=self.api_key)

        self.user_queries = UserQueries()
        self.signal_queries = SignalQueries()
        self.analytics_queries = AnalyticsQueries()

        logger.info("Analytics agent initialized")

    def generate_daily_report(self) -> Dict:
        """
        Generate automated daily business report.

        Returns:
            Daily report with key metrics and insights
        """
        try:
            # Collect metrics
            metrics = self._collect_daily_metrics()

            if not self.client:
                return self._format_basic_report(metrics)

            # Generate AI insights
            insights = self._generate_insights(metrics, period="daily")

            report = {
                "date": datetime.utcnow().date().isoformat(),
                "type": "daily",
                "metrics": metrics,
                "insights": insights,
                "recommendations": self._get_recommendations(metrics, insights),
                "generated_at": datetime.utcnow().isoformat(),
            }

            logger.info("Daily report generated", extra={"metrics": metrics})
            return report

        except Exception as e:
            logger.error(f"Daily report error: {e}")
            return {"error": str(e), "date": datetime.utcnow().date().isoformat()}

    def generate_weekly_report(self) -> Dict:
        """Generate weekly business report."""
        try:
            metrics = self._collect_weekly_metrics()

            if not self.client:
                return self._format_basic_report(metrics)

            insights = self._generate_insights(metrics, period="weekly")

            report = {
                "week": datetime.utcnow().isocalendar().week,
                "year": datetime.utcnow().year,
                "type": "weekly",
                "metrics": metrics,
                "insights": insights,
                "trends": self._analyze_trends(metrics),
                "generated_at": datetime.utcnow().isoformat(),
            }

            logger.info("Weekly report generated")
            return report

        except Exception as e:
            logger.error(f"Weekly report error: {e}")
            return {"error": str(e)}

    def _collect_daily_metrics(self) -> Dict:
        """Collect daily business metrics."""
        today = datetime.utcnow().date()

        # In production, these would query real database
        metrics = {
            "new_users": 5,
            "active_users": 120,
            "signals_generated": 15,
            "signals_delivered": 1800,  # 15 signals × 120 users
            "revenue_today": 2500.0,  # ZAR
            "churn_count": 1,
            "support_tickets": 3,
            "avg_response_time_minutes": 12,
            "email_open_rate": 0.45,
            "telegram_engagement": 0.78,
            "signal_accuracy": 0.94,
            "top_performing_pair": "EURUSD",
        }

        return metrics

    def _collect_weekly_metrics(self) -> Dict:
        """Collect weekly business metrics."""
        metrics = {
            "new_users": 35,
            "total_active_users": 145,
            "mrr": 87500.0,  # Monthly Recurring Revenue in ZAR
            "signals_generated": 105,
            "avg_signal_accuracy": 0.93,
            "churn_rate": 0.08,
            "customer_satisfaction": 4.6,  # out of 5
            "top_plans": {"pro": 60, "basic": 50, "premium": 25, "bot": 8, "enterprise": 2},
            "revenue_growth_pct": 15.0,
        }

        return metrics

    def _generate_insights(self, metrics: Dict, period: str) -> List[str]:
        """Generate AI-powered insights from metrics."""
        if not self.client:
            return ["Metrics collected successfully"]

        try:
            prompt = f"""Analyze these {period} business metrics for Quantum Trading AI and provide actionable insights.

METRICS:
{self._format_metrics_for_prompt(metrics)}

Provide 3-5 key insights focusing on:
1. Performance highlights
2. Areas of concern
3. Growth opportunities
4. Operational improvements

Format as JSON array of strings:
["Insight 1", "Insight 2", "Insight 3"]

Be specific, data-driven, and actionable."""

            response = self.client.messages.create(
                model=settings.claude_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result_text = response.content[0].text
            array_start = result_text.find('[')
            array_end = result_text.rfind(']') + 1

            if array_start >= 0:
                insights = json.loads(result_text[array_start:array_end])
                return insights

            return ["Metrics analyzed successfully"]

        except Exception as e:
            logger.error(f"Insights generation error: {e}")
            return [f"Error generating insights: {e}"]

    def _format_metrics_for_prompt(self, metrics: Dict) -> str:
        """Format metrics for Claude prompt."""
        lines = []
        for key, value in metrics.items():
            if isinstance(value, float):
                if key.endswith('_rate') or key.endswith('_pct'):
                    lines.append(f"- {key}: {value:.1%}")
                elif 'revenue' in key or 'mrr' in key:
                    lines.append(f"- {key}: R{value:,.2f}")
                else:
                    lines.append(f"- {key}: {value:.2f}")
            else:
                lines.append(f"- {key}: {value}")

        return '\n'.join(lines)

    def _get_recommendations(self, metrics: Dict, insights: List[str]) -> List[str]:
        """Get actionable recommendations based on metrics and insights."""
        recommendations = []

        # Rule-based recommendations
        accuracy = metrics.get('signal_accuracy', 0.9)
        if accuracy < 0.90:
            recommendations.append("⚠️ Signal accuracy below target (90%) - Review QPE parameters")

        churn = metrics.get('churn_rate', 0.0)
        if churn > 0.10:
            recommendations.append("📉 Churn rate high (>10%) - Implement retention campaign")

        engagement = metrics.get('telegram_engagement', 0.5)
        if engagement < 0.60:
            recommendations.append("📱 Low Telegram engagement - Improve notification timing")

        new_users = metrics.get('new_users', 0)
        if new_users < 5:
            recommendations.append("👥 Low new user acquisition - Increase marketing spend")

        return recommendations if recommendations else ["✅ All metrics within healthy ranges"]

    def _analyze_trends(self, metrics: Dict) -> Dict:
        """Analyze metric trends."""
        # In production, compare with historical data
        trends = {
            "revenue_trend": "increasing",
            "user_growth_trend": "increasing",
            "accuracy_trend": "stable",
            "churn_trend": "stable",
        }

        return trends

    def _format_basic_report(self, metrics: Dict) -> Dict:
        """Format basic report when Claude unavailable."""
        return {
            "date": datetime.utcnow().date().isoformat(),
            "metrics": metrics,
            "insights": ["Metrics collected successfully"],
            "recommendations": ["Review metrics manually"],
            "generated_at": datetime.utcnow().isoformat(),
        }

    def predict_churn_risk(self, user_id: str) -> Dict:
        """
        Predict churn risk for a user.

        Args:
            user_id: User ID

        Returns:
            Churn prediction with risk score
        """
        try:
            # In production, analyze user behavior patterns
            # For now, return structure
            prediction = {
                "user_id": user_id,
                "churn_risk": "low",  # low, medium, high
                "risk_score": 0.25,  # 0.0-1.0
                "factors": [
                    "Regular engagement with signals",
                    "High Telegram open rate",
                    "Positive support interactions",
                ],
                "recommended_actions": [
                    "Continue standard engagement",
                    "Send monthly performance summary",
                ],
                "predicted_at": datetime.utcnow().isoformat(),
            }

            return prediction

        except Exception as e:
            logger.error(f"Churn prediction error: {e}")
            return {"error": str(e)}

    def forecast_revenue(self, months: int = 3) -> Dict:
        """
        Forecast revenue for next N months.

        Args:
            months: Number of months to forecast

        Returns:
            Revenue forecast
        """
        try:
            # Simple growth-based forecast
            # In production, use time series analysis
            current_mrr = 87500.0  # Current MRR
            growth_rate = 0.15  # 15% monthly growth

            forecast = []
            for month in range(1, months + 1):
                projected_mrr = current_mrr * ((1 + growth_rate) ** month)
                forecast.append({
                    "month": (datetime.utcnow() + timedelta(days=30*month)).strftime("%Y-%m"),
                    "projected_mrr": round(projected_mrr, 2),
                    "confidence": "medium",
                })

            return {
                "forecast_period_months": months,
                "current_mrr": current_mrr,
                "assumed_growth_rate": growth_rate,
                "forecast": forecast,
                "generated_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Revenue forecast error: {e}")
            return {"error": str(e)}

    def get_dashboard_summary(self) -> Dict:
        """
        Get real-time dashboard summary.

        Returns:
            Dashboard metrics summary
        """
        try:
            summary = {
                "current_metrics": {
                    "total_users": 145,
                    "active_subscriptions": 138,
                    "mrr": 87500.0,
                    "signals_today": 15,
                    "avg_accuracy_7d": 0.93,
                },
                "today_activity": {
                    "new_signups": 3,
                    "signals_sent": 1800,
                    "support_tickets": 2,
                    "revenue": 2500.0,
                },
                "trends": {
                    "user_growth_30d": "+25%",
                    "revenue_growth_30d": "+18%",
                    "accuracy_trend": "stable",
                },
                "alerts": self._get_system_alerts(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            return summary

        except Exception as e:
            logger.error(f"Dashboard summary error: {e}")
            return {"error": str(e)}

    def _get_system_alerts(self) -> List[Dict]:
        """Get system alerts and warnings."""
        alerts = []

        # Example alerts
        # In production, check actual system status

        return alerts
