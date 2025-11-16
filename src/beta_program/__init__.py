"""Beta testing program management."""

from .application import BetaApplicationManager
from .feedback import FeedbackCollector
from .monitoring import PerformanceMonitor
from .graduation import BetaGraduation

__all__ = [
    "BetaApplicationManager",
    "FeedbackCollector",
    "PerformanceMonitor",
    "BetaGraduation",
]

__version__ = "3.0.0"  # Phase 3 - Beta Testing
