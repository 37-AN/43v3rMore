"""Quantum trading engine for high-accuracy signal generation."""

from .engine import QuantumTradingEngine
from .signal_generator import SignalGenerator
from .mt5_connector import MT5Connector
from .qpe import QuantumPhaseEstimator
from .optimizer import SignalOptimizer

__all__ = [
    "QuantumTradingEngine",
    "SignalGenerator",
    "MT5Connector",
    "QuantumPhaseEstimator",
    "SignalOptimizer",
]

__version__ = "1.0.0"
