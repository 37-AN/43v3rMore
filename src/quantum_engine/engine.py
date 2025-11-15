"""Main Quantum Trading Engine orchestrating all components."""

from typing import List, Optional, Dict
from datetime import datetime, timezone, timezone
import pandas as pd
from loguru import logger

from .mt5_connector import MT5Connector
from .signal_generator import SignalGenerator, TradingSignal
from .qpe import QuantumPhaseEstimator
from ..utils.config import get_settings


class QuantumTradingEngine:
    """
    Main trading engine coordinating quantum analysis and signal generation.

    Integrates MT5 data, QPE analysis, and signal generation for
    autonomous trading operations.
    """

    def __init__(
        self,
        symbols: Optional[List[str]] = None,
        confidence_threshold: Optional[float] = None,
        num_qubits: int = 4,
        lookback_period: int = 100,
    ):
        """
        Initialize Quantum Trading Engine.

        Args:
            symbols: List of trading symbols (default: from settings)
            confidence_threshold: Minimum signal confidence (default: from settings)
            num_qubits: QPE precision
            lookback_period: Historical data window

        Example:
            >>> engine = QuantumTradingEngine(symbols=["EURUSD", "GBPUSD"])
            >>> signals = engine.analyze_all_symbols()
        """
        settings = get_settings()

        self.symbols = symbols or settings.symbols_list
        self.confidence_threshold = (
            confidence_threshold or settings.signal_confidence_threshold
        )
        self.lookback_period = lookback_period

        # Initialize components
        self.mt5 = MT5Connector(
            login=settings.mt5_login if settings.mt5_login else None,
            password=settings.mt5_password if settings.mt5_password else None,
            server=settings.mt5_server if settings.mt5_server else None,
            timeout=settings.mt5_timeout,
        )

        self.signal_generator = SignalGenerator(
            confidence_threshold=self.confidence_threshold,
            num_qubits=num_qubits,
            lookback_period=lookback_period,
        )

        self.qpe = QuantumPhaseEstimator(num_qubits=num_qubits)

        logger.info(
            f"QuantumTradingEngine initialized: {len(self.symbols)} symbols",
            extra={
                "symbols": self.symbols,
                "confidence_threshold": self.confidence_threshold,
                "num_qubits": num_qubits,
            },
        )

    def start(self) -> bool:
        """
        Start the trading engine.

        Returns:
            True if started successfully

        Example:
            >>> engine.start()
            >>> # Engine running...
            >>> engine.stop()
        """
        logger.info("Starting Quantum Trading Engine...")

        # Connect to MT5
        if self.mt5.connect():
            logger.info("✓ MT5 connected")
        else:
            logger.warning("✗ MT5 not connected (using mock data)")

        logger.info("Quantum Trading Engine started")
        return True

    def stop(self) -> None:
        """
        Stop the trading engine.

        Example:
            >>> engine.stop()
        """
        logger.info("Stopping Quantum Trading Engine...")
        self.mt5.disconnect()
        logger.info("Quantum Trading Engine stopped")

    def analyze_symbol(
        self,
        symbol: str,
        timeframe: str = "H1",
    ) -> Optional[TradingSignal]:
        """
        Analyze single symbol and generate signal.

        Args:
            symbol: Trading symbol
            timeframe: Analysis timeframe

        Returns:
            TradingSignal or None

        Example:
            >>> signal = engine.analyze_symbol("EURUSD", "H1")
            >>> if signal:
            ...     print(f"{signal.action} @ {signal.entry_price}")
        """
        try:
            logger.info(f"Analyzing {symbol} {timeframe}...")

            # Get market data
            data = self.mt5.get_rates(
                symbol=symbol,
                timeframe=timeframe,
                count=self.lookback_period + 50,
            )

            if data is None or len(data) < self.lookback_period:
                logger.warning(f"Insufficient data for {symbol}")
                return None

            # Generate signal
            signal = self.signal_generator.generate(data, symbol)

            if signal:
                logger.info(
                    f"Signal: {signal.action} {symbol} @ {signal.entry_price:.5f} ({signal.confidence:.2%})"
                )
            else:
                logger.debug(f"No signal for {symbol}")

            return signal

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None

    def analyze_all_symbols(
        self,
        timeframe: str = "H1",
    ) -> List[TradingSignal]:
        """
        Analyze all symbols and generate signals.

        Args:
            timeframe: Analysis timeframe

        Returns:
            List of TradingSignals

        Example:
            >>> signals = engine.analyze_all_symbols()
            >>> for signal in signals:
            ...     print(f"{signal.symbol}: {signal.action}")
        """
        logger.info(f"Analyzing {len(self.symbols)} symbols on {timeframe}...")

        signals = []
        symbols_data = {}

        # Collect data for all symbols
        for symbol in self.symbols:
            try:
                data = self.mt5.get_rates(
                    symbol=symbol,
                    timeframe=timeframe,
                    count=self.lookback_period + 50,
                )

                if data is not None and len(data) >= self.lookback_period:
                    symbols_data[symbol] = data
                else:
                    logger.warning(f"Skipping {symbol}: insufficient data")

            except Exception as e:
                logger.error(f"Error getting data for {symbol}: {e}")

        # Generate signals in batch
        if symbols_data:
            signals = self.signal_generator.generate_batch(symbols_data)

        logger.info(
            f"Analysis complete: {len(signals)} signals generated",
            extra={
                "total_symbols": len(self.symbols),
                "analyzed_symbols": len(symbols_data),
                "signals_generated": len(signals),
            },
        )

        return signals

    def get_market_summary(self) -> Dict:
        """
        Get current market summary.

        Returns:
            Market summary dictionary

        Example:
            >>> summary = engine.get_market_summary()
            >>> print(summary['symbols_analyzed'])
        """
        try:
            summary = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "symbols_configured": len(self.symbols),
                "mt5_connected": self.mt5.connected,
                "confidence_threshold": self.confidence_threshold,
            }

            # Get current prices
            current_prices = {}
            for symbol in self.symbols[:5]:  # Limit to first 5
                price = self.mt5.get_current_price(symbol)
                if price:
                    current_prices[symbol] = price

            summary["current_prices"] = current_prices

            return summary

        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {}

    def run_analysis_cycle(
        self,
        timeframe: str = "H1",
        max_signals: Optional[int] = None,
    ) -> Dict:
        """
        Run complete analysis cycle.

        Args:
            timeframe: Analysis timeframe
            max_signals: Maximum signals to generate

        Returns:
            Analysis results

        Example:
            >>> results = engine.run_analysis_cycle(max_signals=5)
            >>> print(f"Generated {len(results['signals'])} signals")
        """
        logger.info("Starting analysis cycle...")

        # Analyze all symbols
        signals = self.analyze_all_symbols(timeframe=timeframe)

        # Limit signals if specified
        if max_signals and len(signals) > max_signals:
            # Sort by confidence and take top N
            signals.sort(key=lambda s: s.confidence, reverse=True)
            signals = signals[:max_signals]
            logger.info(f"Limited to top {max_signals} signals")

        # Prepare results
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbols_analyzed": len(self.symbols),
            "signals_generated": len(signals),
            "signals": [s.to_dict() for s in signals],
            "timeframe": timeframe,
        }

        logger.info(
            f"Analysis cycle complete: {len(signals)} signals",
            extra={"signals_count": len(signals)},
        )

        return results

    def validate_system(self) -> Dict[str, bool]:
        """
        Validate all system components.

        Returns:
            Validation results

        Example:
            >>> validation = engine.validate_system()
            >>> if all(validation.values()):
            ...     print("All systems operational")
        """
        logger.info("Validating system components...")

        validation = {
            "mt5_available": self.mt5.connected or not MT5Connector,
            "symbols_configured": len(self.symbols) > 0,
            "qpe_initialized": self.qpe is not None,
            "signal_generator_ready": self.signal_generator is not None,
        }

        # Test signal generation with mock data
        try:
            test_data = self.mt5._generate_mock_data("EURUSD", 100)
            test_signal = self.signal_generator.generate(test_data, "EURUSD")
            validation["signal_generation_working"] = test_signal is not None
        except Exception as e:
            logger.error(f"Signal generation test failed: {e}")
            validation["signal_generation_working"] = False

        all_valid = all(validation.values())

        logger.info(
            f"System validation: {'PASSED' if all_valid else 'FAILED'}",
            extra=validation,
        )

        return validation

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
