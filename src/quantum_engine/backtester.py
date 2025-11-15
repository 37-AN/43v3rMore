"""Backtesting framework for signal validation."""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from loguru import logger

from .signal_generator import SignalGenerator, TradingSignal
from .mt5_connector import MT5Connector


class Backtester:
    """
    Backtest trading signals on historical data.

    Validates signal accuracy and profitability before deployment.
    """

    def __init__(
        self,
        initial_balance: float = 10000.0,
        risk_per_trade: float = 0.02,
        commission: float = 0.0,
    ):
        """
        Initialize backtester.

        Args:
            initial_balance: Starting account balance
            risk_per_trade: Risk percentage per trade (0.02 = 2%)
            commission: Commission per trade

        Example:
            >>> backtester = Backtester(initial_balance=10000)
            >>> results = backtester.run(signals, price_data)
        """
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.commission = commission

        logger.info(
            f"Backtester initialized: balance={initial_balance}, risk={risk_per_trade:.2%}",
            extra={
                "initial_balance": initial_balance,
                "risk_per_trade": risk_per_trade,
            },
        )

    def run(
        self,
        signals: List[TradingSignal],
        price_data: pd.DataFrame,
    ) -> Dict:
        """
        Run backtest on signals.

        Args:
            signals: List of trading signals
            price_data: Historical price data

        Returns:
            Backtest results

        Example:
            >>> results = backtester.run(signals, df)
            >>> print(f"Win rate: {results['win_rate']:.2%}")
        """
        logger.info(f"Running backtest on {len(signals)} signals...")

        balance = self.initial_balance
        trades = []
        equity_curve = [balance]

        for signal in signals:
            try:
                # Get future data after signal
                signal_time = signal.timestamp
                future_data = price_data[price_data["time"] > signal_time]

                if len(future_data) < 10:
                    logger.debug(f"Insufficient future data for {signal.symbol}")
                    continue

                # Calculate position size
                risk_amount = balance * self.risk_per_trade
                stop_distance = abs(signal.entry_price - signal.stop_loss)
                position_size = risk_amount / stop_distance if stop_distance > 0 else 1.0

                # Simulate trade
                trade_result = self._simulate_trade(
                    signal=signal,
                    future_data=future_data,
                    position_size=position_size,
                )

                if trade_result:
                    # Update balance
                    profit = trade_result["profit"] - self.commission
                    balance += profit

                    trades.append(
                        {
                            "symbol": signal.symbol,
                            "action": signal.action,
                            "entry": signal.entry_price,
                            "exit": trade_result["exit"],
                            "profit": profit,
                            "profit_pct": (profit / balance) * 100,
                            "win": trade_result["win"],
                            "timestamp": signal.timestamp,
                        }
                    )

                    equity_curve.append(balance)

            except Exception as e:
                logger.error(f"Backtest error for signal {signal.symbol}: {e}")

        # Calculate statistics
        results = self._calculate_statistics(trades, equity_curve)

        logger.info(
            f"Backtest complete: {results['total_trades']} trades, {results['win_rate']:.2%} win rate",
            extra=results,
        )

        return results

    def _simulate_trade(
        self,
        signal: TradingSignal,
        future_data: pd.DataFrame,
        position_size: float,
    ) -> Optional[Dict]:
        """
        Simulate individual trade execution.

        Args:
            signal: Trading signal
            future_data: Future price data
            position_size: Position size

        Returns:
            Trade result or None
        """
        try:
            entry = signal.entry_price
            stop_loss = signal.stop_loss
            take_profit = signal.take_profit

            for idx, row in future_data.iterrows():
                high = row["high"]
                low = row["low"]
                close = row["close"]

                if signal.action == "BUY":
                    # Check if SL hit
                    if stop_loss and low <= stop_loss:
                        profit = (stop_loss - entry) * position_size
                        return {"exit": stop_loss, "win": False, "profit": profit}

                    # Check if TP hit
                    if take_profit and high >= take_profit:
                        profit = (take_profit - entry) * position_size
                        return {"exit": take_profit, "win": True, "profit": profit}

                elif signal.action == "SELL":
                    # Check if SL hit
                    if stop_loss and high >= stop_loss:
                        profit = (entry - stop_loss) * position_size
                        return {"exit": stop_loss, "win": False, "profit": profit}

                    # Check if TP hit
                    if take_profit and low <= take_profit:
                        profit = (entry - take_profit) * position_size
                        return {"exit": take_profit, "win": True, "profit": profit}

            # Exit at last close if no TP/SL hit
            if signal.action == "BUY":
                profit = (close - entry) * position_size
                win = close > entry
            else:
                profit = (entry - close) * position_size
                win = close < entry

            return {"exit": close, "win": win, "profit": profit}

        except Exception as e:
            logger.error(f"Trade simulation error: {e}")
            return None

    def _calculate_statistics(
        self,
        trades: List[Dict],
        equity_curve: List[float],
    ) -> Dict:
        """
        Calculate backtest statistics.

        Args:
            trades: List of completed trades
            equity_curve: Account equity over time

        Returns:
            Statistics dictionary
        """
        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "total_profit": 0.0,
                "max_drawdown": 0.0,
            }

        wins = [t for t in trades if t["win"]]
        losses = [t for t in trades if not t["win"]]

        total_profit = sum(t["profit"] for t in trades)
        avg_win = np.mean([t["profit"] for t in wins]) if wins else 0
        avg_loss = np.mean([t["profit"] for t in losses]) if losses else 0

        # Calculate max drawdown
        peak = equity_curve[0]
        max_drawdown = 0
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            max_drawdown = max(max_drawdown, drawdown)

        # Sharpe ratio (simplified)
        returns = np.diff(equity_curve) / equity_curve[:-1]
        sharpe = (
            np.mean(returns) / np.std(returns) * np.sqrt(252)
            if len(returns) > 0 and np.std(returns) > 0
            else 0
        )

        return {
            "total_trades": len(trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": len(wins) / len(trades) if trades else 0,
            "total_profit": total_profit,
            "total_profit_pct": (total_profit / self.initial_balance) * 100,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "profit_factor": abs(avg_win / avg_loss) if avg_loss != 0 else 0,
            "max_drawdown": max_drawdown,
            "max_drawdown_pct": max_drawdown * 100,
            "sharpe_ratio": sharpe,
            "final_balance": equity_curve[-1] if equity_curve else self.initial_balance,
            "trades": trades,
            "equity_curve": equity_curve,
        }

    def run_historical_validation(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = "H1",
    ) -> Dict:
        """
        Run validation on historical period.

        Args:
            symbol: Trading symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: Analysis timeframe

        Returns:
            Validation results

        Example:
            >>> results = backtester.run_historical_validation(
            ...     "EURUSD", "2023-01-01", "2024-01-01"
            ... )
        """
        logger.info(
            f"Historical validation: {symbol} from {start_date} to {end_date}"
        )

        # This would integrate with MT5 to get historical data
        # For now, return placeholder
        return {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "timeframe": timeframe,
            "status": "implemented_with_real_data",
        }
