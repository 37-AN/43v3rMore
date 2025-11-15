"""Tests for quantum trading engine."""

import pytest
from src.quantum_engine import QuantumPhaseEstimator, SignalGenerator, MT5Connector


def test_qpe_initialization():
    """Test QPE initialization."""
    qpe = QuantumPhaseEstimator(num_qubits=4)
    assert qpe.num_qubits == 4
    assert qpe.shots == 1024


def test_qpe_encode_price_data():
    """Test price data encoding."""
    qpe = QuantumPhaseEstimator()
    prices = [1.1000, 1.1050, 1.1100, 1.1080, 1.1120]

    phase = qpe.encode_price_data(prices)
    assert isinstance(phase, float)
    assert 0 <= phase <= 2 * 3.14159


def test_signal_generator_initialization():
    """Test signal generator initialization."""
    generator = SignalGenerator(confidence_threshold=0.75)
    assert generator.confidence_threshold == 0.75


def test_signal_generation(mock_price_data):
    """Test signal generation."""
    generator = SignalGenerator(confidence_threshold=0.5)
    signal = generator.generate(mock_price_data, "EURUSD")

    # Signal might be None or a valid signal
    if signal:
        assert signal.symbol == "EURUSD"
        assert signal.action in ["BUY", "SELL", "HOLD"]
        assert 0 <= signal.confidence <= 1.0


def test_mt5_connector_mock_data():
    """Test MT5 connector with mock data."""
    connector = MT5Connector()
    data = connector._generate_mock_data("EURUSD", 100)

    assert len(data) == 100
    assert "close" in data.columns
    assert "open" in data.columns
