"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.utils.config import get_settings


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def settings():
    """Get settings instance."""
    return get_settings()


@pytest.fixture
def mock_signal_data():
    """Mock trading signal data."""
    return {
        "symbol": "EURUSD",
        "action": "BUY",
        "confidence": 0.87,
        "entry_price": 1.1000,
        "stop_loss": 1.0950,
        "take_profit": 1.1100,
        "risk_reward": 2.0,
        "timeframe": "H1",
        "reason": "Bullish cycle detected",
    }


@pytest.fixture
def mock_user_data():
    """Mock user data."""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "plan": "basic",
        "status": "active",
    }


@pytest.fixture
def mock_price_data():
    """Mock price data for testing."""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta

    dates = pd.date_range(end=datetime.now(), periods=100, freq="h")
    prices = 1.1000 + np.cumsum(np.random.randn(100) * 0.001)

    return pd.DataFrame({
        "time": dates,
        "open": prices,
        "high": prices * 1.001,
        "low": prices * 0.999,
        "close": prices,
        "tick_volume": np.random.randint(100, 1000, 100),
    })
