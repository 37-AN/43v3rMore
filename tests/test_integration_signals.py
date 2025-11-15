"""Integration tests for signal generation flow."""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.quantum_engine import QuantumTradingEngine, SignalGenerator, MT5Connector
from src.quantum_engine.qpe import QuantumPhaseEstimator
from src.quantum_engine.backtester import Backtester


class TestSignalGenerationFlow:
    """Test complete signal generation flow."""

    def test_end_to_end_signal_generation(self):
        """Test complete signal generation from data to signal."""
        # 1. Generate mock price data
        connector = MT5Connector()
        price_data = connector._generate_mock_data("EURUSD", 100)

        assert len(price_data) == 100
        assert "close" in price_data.columns

        # 2. Generate signal
        generator = SignalGenerator(confidence_threshold=0.5)
        signal = generator.generate(price_data, "EURUSD")

        # Signal may be None or valid signal
        if signal:
            assert signal.symbol == "EURUSD"
            assert signal.action in ["BUY", "SELL", "HOLD"]
            assert 0 <= signal.confidence <= 1.0
            assert signal.entry_price > 0

            # Verify risk management
            if signal.action == "BUY" and signal.stop_loss:
                assert signal.stop_loss < signal.entry_price
                if signal.take_profit:
                    assert signal.take_profit > signal.entry_price

            elif signal.action == "SELL" and signal.stop_loss:
                assert signal.stop_loss > signal.entry_price
                if signal.take_profit:
                    assert signal.take_profit < signal.entry_price

    def test_quantum_engine_analysis(self):
        """Test quantum trading engine analysis."""
        engine = QuantumTradingEngine(
            symbols=["EURUSD"],
            confidence_threshold=0.5,
        )

        # Start engine (uses mock data)
        engine.start()

        # Analyze symbol
        signal = engine.analyze_symbol("EURUSD", timeframe="H1")

        # Signal may be None or valid
        if signal:
            assert signal.symbol == "EURUSD"
            assert hasattr(signal, "confidence")

        # Stop engine
        engine.stop()

    def test_batch_signal_generation(self):
        """Test generating signals for multiple symbols."""
        generator = SignalGenerator(confidence_threshold=0.5)

        # Generate data for multiple symbols
        symbols_data = {}
        for symbol in ["EURUSD", "GBPUSD", "USDJPY"]:
            connector = MT5Connector()
            symbols_data[symbol] = connector._generate_mock_data(symbol, 100)

        # Generate batch signals
        signals = generator.generate_batch(symbols_data)

        assert isinstance(signals, list)
        # Signals list may be empty if no high-confidence signals

        for signal in signals:
            assert signal.symbol in ["EURUSD", "GBPUSD", "USDJPY"]
            assert signal.confidence >= 0.5  # Threshold

    def test_signal_with_metadata(self):
        """Test signal generation includes metadata."""
        connector = MT5Connector()
        price_data = connector._generate_mock_data("XAUUSD", 100)

        generator = SignalGenerator()
        signal = generator.generate(price_data, "XAUUSD")

        if signal:
            assert hasattr(signal, "metadata")
            assert isinstance(signal.metadata, dict)
            assert hasattr(signal, "reason")
            assert isinstance(signal.reason, str)
            assert hasattr(signal, "created_at")


class TestQuantumPhaseEstimator:
    """Test QPE component."""

    def test_qpe_cycle_detection(self):
        """Test QPE cycle detection."""
        qpe = QuantumPhaseEstimator(num_qubits=4)

        # Generate trending price data
        base_price = 1.1000
        prices = [base_price + i * 0.0001 for i in range(50)]

        # Detect cycle
        cycle = qpe.detect_cycle(prices, window=20)

        assert "period" in cycle
        assert "strength" in cycle
        assert "direction" in cycle
        assert cycle["direction"] in ["bullish", "bearish", "neutral"]
        assert 0 <= cycle["strength"] <= 1.0

    def test_qpe_phase_estimation(self):
        """Test phase estimation."""
        qpe = QuantumPhaseEstimator(num_qubits=4)

        # Generate price data
        prices = [1.1000 + np.sin(i * 0.1) * 0.01 for i in range(100)]

        # Estimate phase
        result = qpe.estimate_phase(prices)

        assert "phase" in result
        assert "confidence" in result
        assert "measurements" in result
        assert 0 <= result["confidence"] <= 1.0


class TestBacktesting:
    """Test backtesting framework."""

    def test_backtester_initialization(self):
        """Test backtester initialization."""
        backtester = Backtester(
            initial_balance=10000.0,
            risk_per_trade=0.02,
        )

        assert backtester.initial_balance == 10000.0
        assert backtester.risk_per_trade == 0.02

    def test_signal_backtesting(self, mock_signal_data, mock_price_data):
        """Test backtesting individual signal."""
        from src.quantum_engine.signal_generator import TradingSignal

        # Create signal (remove timeframe as it's not in TradingSignal)
        signal_data = {k: v for k, v in mock_signal_data.items() if k != 'timeframe'}
        signal = TradingSignal(**signal_data)

        # Create future price data
        future_data = mock_price_data.copy()

        # Backtest signal
        generator = SignalGenerator()
        result = generator.backtest_signal(signal, future_data, periods=50)

        assert "win" in result
        assert "profit_pct" in result
        assert isinstance(result["win"], bool)
        assert isinstance(result["profit_pct"], float)


class TestMT5Connector:
    """Test MT5 connector."""

    def test_mock_data_generation(self):
        """Test mock data generation."""
        connector = MT5Connector()
        data = connector._generate_mock_data("EURUSD", 100)

        assert len(data) == 100
        assert all(col in data.columns for col in ["open", "high", "low", "close", "tick_volume"])

        # Verify OHLC consistency
        assert (data["high"] >= data["low"]).all()
        assert (data["high"] >= data["open"]).all()
        assert (data["high"] >= data["close"]).all()
        assert (data["low"] <= data["open"]).all()
        assert (data["low"] <= data["close"]).all()

    def test_multiple_symbols_mock_data(self):
        """Test generating mock data for different symbols."""
        connector = MT5Connector()

        for symbol in ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD"]:
            data = connector._generate_mock_data(symbol, 50)
            assert len(data) == 50
            assert "close" in data.columns

    def test_price_volatility(self):
        """Test that mock data has realistic volatility."""
        connector = MT5Connector()
        data = connector._generate_mock_data("EURUSD", 100)

        # Calculate returns
        returns = data["close"].pct_change().dropna()

        # Check volatility is reasonable (not too high or too low)
        volatility = returns.std()
        assert 0.0001 < volatility < 0.01  # Realistic for hourly forex data


class TestSystemValidation:
    """Test system validation."""

    def test_engine_validation(self):
        """Test quantum engine validation."""
        engine = QuantumTradingEngine(symbols=["EURUSD"])

        validation = engine.validate_system()

        assert isinstance(validation, dict)
        assert "symbols_configured" in validation
        assert validation["symbols_configured"] is True
        assert "qpe_initialized" in validation
        assert "signal_generator_ready" in validation

    def test_market_summary(self):
        """Test market summary generation."""
        engine = QuantumTradingEngine(symbols=["EURUSD", "GBPUSD"])

        summary = engine.get_market_summary()

        assert isinstance(summary, dict)
        assert "symbols_configured" in summary
        assert summary["symbols_configured"] == 2

    def test_analysis_cycle(self):
        """Test complete analysis cycle."""
        engine = QuantumTradingEngine(
            symbols=["EURUSD"],
            confidence_threshold=0.5,
        )

        engine.start()
        results = engine.run_analysis_cycle(timeframe="H1", max_signals=5)
        engine.stop()

        assert isinstance(results, dict)
        assert "timestamp" in results
        assert "symbols_analyzed" in results
        assert "signals_generated" in results
        assert "signals" in results
        assert isinstance(results["signals"], list)
