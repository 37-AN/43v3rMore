"""Trading signal generation using quantum analysis."""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timezone
import numpy as np
import pandas as pd
from loguru import logger

from .qpe import QuantumPhaseEstimator


@dataclass
class TradingSignal:
    """Trading signal data structure."""

    symbol: str
    action: str  # BUY, SELL, HOLD
    confidence: float  # 0.0 to 1.0
    entry_price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    risk_reward: Optional[float] = None
    timestamp: datetime = None
    reason: str = ""
    metadata: Dict = None

    def __post_init__(self):
        """Initialize default values."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class SignalGenerator:
    """
    Generate trading signals using quantum phase estimation.

    Analyzes market cycles and generates high-confidence signals.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.75,
        num_qubits: int = 4,
        lookback_period: int = 100,
    ):
        """
        Initialize signal generator.

        Args:
            confidence_threshold: Minimum confidence for signals
            num_qubits: QPE precision
            lookback_period: Historical data window

        Example:
            >>> generator = SignalGenerator(confidence_threshold=0.80)
            >>> signal = generator.generate(df, "EURUSD")
        """
        self.confidence_threshold = confidence_threshold
        self.lookback_period = lookback_period
        self.qpe = QuantumPhaseEstimator(num_qubits=num_qubits)

        logger.info(
            f"SignalGenerator initialized: threshold={confidence_threshold}",
            extra={
                "confidence_threshold": confidence_threshold,
                "num_qubits": num_qubits,
                "lookback_period": lookback_period,
            },
        )

    def generate(
        self,
        price_data: pd.DataFrame,
        symbol: str,
    ) -> Optional[TradingSignal]:
        """
        Generate trading signal from price data.

        Args:
            price_data: DataFrame with OHLCV data
            symbol: Trading symbol

        Returns:
            TradingSignal or None

        Example:
            >>> signal = generator.generate(df, "EURUSD")
            >>> if signal and signal.action != "HOLD":
            ...     print(f"{signal.action} {signal.symbol}")
        """
        try:
            if len(price_data) < self.lookback_period:
                logger.warning(
                    f"Insufficient data for {symbol}: {len(price_data)} < {self.lookback_period}"
                )
                return None

            # Extract close prices
            prices = price_data["close"].tail(self.lookback_period).values

            # Detect market cycle
            cycle = self.qpe.detect_cycle(prices)

            # Current price
            current_price = float(prices[-1])

            # Calculate signal parameters
            signal = self._analyze_cycle(
                symbol=symbol,
                current_price=current_price,
                cycle=cycle,
                prices=prices,
            )

            if signal and signal.confidence >= self.confidence_threshold:
                logger.info(
                    f"Signal generated: {signal.action} {symbol} @ {signal.entry_price:.5f} ({signal.confidence:.2%})",
                    extra={
                        "symbol": symbol,
                        "action": signal.action,
                        "confidence": signal.confidence,
                    },
                )
                return signal
            else:
                logger.debug(f"No high-confidence signal for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Signal generation error for {symbol}: {e}")
            return None

    def _analyze_cycle(
        self,
        symbol: str,
        current_price: float,
        cycle: Dict,
        prices: np.ndarray,
    ) -> Optional[TradingSignal]:
        """
        Analyze cycle data to generate signal.

        Args:
            symbol: Trading symbol
            current_price: Current market price
            cycle: Cycle detection results
            prices: Price history

        Returns:
            TradingSignal or None
        """
        try:
            # Extract cycle parameters
            period = cycle.get("period", 0)
            strength = cycle.get("strength", 0)
            direction = cycle.get("direction", "neutral")
            phase = cycle.get("phase", 0)

            # Calculate technical indicators
            sma_20 = np.mean(prices[-20:])
            sma_50 = np.mean(prices[-50:]) if len(prices) >= 50 else sma_20
            volatility = np.std(prices[-20:]) / np.mean(prices[-20:])

            # Signal logic
            if strength < self.confidence_threshold:
                return TradingSignal(
                    symbol=symbol,
                    action="HOLD",
                    confidence=strength,
                    entry_price=current_price,
                    reason="Low cycle strength",
                    metadata=cycle,
                )

            # Bullish signal
            if direction == "bullish" and current_price > sma_20:
                stop_loss = current_price * (1 - 2 * volatility)
                take_profit = current_price * (1 + 4 * volatility)
                risk_reward = abs(take_profit - current_price) / abs(current_price - stop_loss)

                return TradingSignal(
                    symbol=symbol,
                    action="BUY",
                    confidence=strength,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_reward=risk_reward,
                    reason=f"Bullish cycle (period={period:.1f}, phase={phase:.2f})",
                    metadata={
                        **cycle,
                        "sma_20": sma_20,
                        "sma_50": sma_50,
                        "volatility": volatility,
                    },
                )

            # Bearish signal
            elif direction == "bearish" and current_price < sma_20:
                stop_loss = current_price * (1 + 2 * volatility)
                take_profit = current_price * (1 - 4 * volatility)
                risk_reward = abs(current_price - take_profit) / abs(stop_loss - current_price)

                return TradingSignal(
                    symbol=symbol,
                    action="SELL",
                    confidence=strength,
                    entry_price=current_price,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    risk_reward=risk_reward,
                    reason=f"Bearish cycle (period={period:.1f}, phase={phase:.2f})",
                    metadata={
                        **cycle,
                        "sma_20": sma_20,
                        "sma_50": sma_50,
                        "volatility": volatility,
                    },
                )

            else:
                return TradingSignal(
                    symbol=symbol,
                    action="HOLD",
                    confidence=strength,
                    entry_price=current_price,
                    reason="Conflicting indicators",
                    metadata=cycle,
                )

        except Exception as e:
            logger.error(f"Cycle analysis error: {e}")
            return None

    def generate_batch(
        self,
        symbols_data: Dict[str, pd.DataFrame],
    ) -> List[TradingSignal]:
        """
        Generate signals for multiple symbols.

        Args:
            symbols_data: Dict mapping symbols to DataFrames

        Returns:
            List of TradingSignals

        Example:
            >>> data = {"EURUSD": df1, "GBPUSD": df2}
            >>> signals = generator.generate_batch(data)
        """
        signals = []

        for symbol, data in symbols_data.items():
            try:
                signal = self.generate(data, symbol)
                if signal and signal.action != "HOLD":
                    signals.append(signal)
            except Exception as e:
                logger.error(f"Batch signal error for {symbol}: {e}")

        logger.info(
            f"Generated {len(signals)} signals from {len(symbols_data)} symbols",
            extra={"signals_count": len(signals), "symbols_count": len(symbols_data)},
        )

        return signals

    def backtest_signal(
        self,
        signal: TradingSignal,
        future_data: pd.DataFrame,
        periods: int = 50,
    ) -> Dict:
        """
        Backtest signal performance.

        Args:
            signal: Trading signal to test
            future_data: Future price data
            periods: Number of periods to test

        Returns:
            Backtest results

        Example:
            >>> results = generator.backtest_signal(signal, future_df)
            >>> print(f"Win: {results['win']}, Profit: {results['profit_pct']}")
        """
        try:
            if len(future_data) < periods:
                periods = len(future_data)

            prices = future_data["close"].head(periods).values
            entry = signal.entry_price

            if signal.action == "BUY":
                max_price = np.max(prices)
                min_price = np.min(prices)

                hit_tp = bool(max_price >= signal.take_profit) if signal.take_profit else False
                hit_sl = bool(min_price <= signal.stop_loss) if signal.stop_loss else False

                if hit_sl:
                    exit_price = signal.stop_loss
                    win = False
                elif hit_tp:
                    exit_price = signal.take_profit
                    win = True
                else:
                    exit_price = prices[-1]
                    win = bool(exit_price > entry)

            else:  # SELL
                max_price = np.max(prices)
                min_price = np.min(prices)

                hit_tp = bool(min_price <= signal.take_profit) if signal.take_profit else False
                hit_sl = bool(max_price >= signal.stop_loss) if signal.stop_loss else False

                if hit_sl:
                    exit_price = signal.stop_loss
                    win = False
                elif hit_tp:
                    exit_price = signal.take_profit
                    win = True
                else:
                    exit_price = prices[-1]
                    win = bool(exit_price < entry)

            profit_pct = ((exit_price - entry) / entry) * 100
            if signal.action == "SELL":
                profit_pct = -profit_pct

            return {
                "win": win,
                "entry": entry,
                "exit": exit_price,
                "profit_pct": profit_pct,
                "hit_tp": hit_tp,
                "hit_sl": hit_sl,
                "periods": periods,
            }

        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return {"win": False, "profit_pct": 0.0}
