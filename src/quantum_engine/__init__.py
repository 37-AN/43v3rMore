"""Quantum trading engine for high-accuracy signal generation."""

from .engine import QuantumTradingEngine
from .signal_generator import SignalGenerator
from .mt5_connector import MT5Connector
from .qpe import QuantumPhaseEstimator

__all__ = [
    "QuantumTradingEngine",
    "SignalGenerator",
    "MT5Connector",
    "QuantumPhaseEstimator",
]

__version__ = "1.0.0"
