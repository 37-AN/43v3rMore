"""General helper utilities."""

from typing import Optional, Union
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone, timezone
from loguru import logger


def format_currency(
    amount: Union[int, float, Decimal],
    currency: str = "ZAR",
    decimals: int = 2,
) -> str:
    """
    Format amount as currency string.

    Args:
        amount: Amount to format
        currency: Currency code
        decimals: Number of decimal places

    Returns:
        Formatted currency string

    Example:
        >>> format_currency(1234.56, "ZAR")
        'R1,234.56'
        >>> format_currency(1000, "USD")
        '$1,000.00'
    """
    symbols = {
        "ZAR": "R",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }

    symbol = symbols.get(currency.upper(), currency)

    try:
        amount_decimal = Decimal(str(amount))
        formatted_amount = f"{amount_decimal:,.{decimals}f}"
        return f"{symbol}{formatted_amount}"
    except Exception as e:
        logger.error(f"Currency formatting error: {e}")
        return f"{symbol}{amount}"


def calculate_percentage(
    value: Union[int, float],
    total: Union[int, float],
    decimals: int = 2,
) -> float:
    """
    Calculate percentage with safe division.

    Args:
        value: Part value
        total: Total value
        decimals: Decimal places to round

    Returns:
        Percentage value

    Example:
        >>> calculate_percentage(25, 100)
        25.0
        >>> calculate_percentage(1, 3, decimals=1)
        33.3
    """
    if total == 0:
        logger.warning("Division by zero in percentage calculation")
        return 0.0

    try:
        percentage = (value / total) * 100
        return round(percentage, decimals)
    except Exception as e:
        logger.error(f"Percentage calculation error: {e}")
        return 0.0


def safe_divide(
    numerator: Union[int, float],
    denominator: Union[int, float],
    default: float = 0.0,
) -> float:
    """
    Perform safe division with fallback.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division fails

    Returns:
        Division result or default

    Example:
        >>> safe_divide(10, 2)
        5.0
        >>> safe_divide(10, 0, default=0)
        0.0
    """
    if denominator == 0:
        logger.warning(f"Division by zero: {numerator} / {denominator}")
        return default

    try:
        return numerator / denominator
    except Exception as e:
        logger.error(f"Division error: {e}")
        return default


def get_utc_now() -> datetime:
    """
    Get current UTC datetime.

    Returns:
        Current UTC datetime with timezone

    Example:
        >>> now = get_utc_now()
        >>> print(now.tzinfo)
        UTC
    """
    return datetime.now(timezone.utc)


def format_datetime(
    dt: datetime,
    format_str: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """
    Format datetime to string.

    Args:
        dt: Datetime to format
        format_str: Format string

    Returns:
        Formatted datetime string

    Example:
        >>> dt = datetime(2025, 1, 1, 12, 0, 0)
        >>> format_datetime(dt)
        '2025-01-01 12:00:00'
    """
    try:
        return dt.strftime(format_str)
    except Exception as e:
        logger.error(f"Datetime formatting error: {e}")
        return str(dt)


def truncate_string(
    text: str,
    max_length: int = 50,
    suffix: str = "...",
) -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string

    Example:
        >>> truncate_string("This is a very long text", 10)
        'This is...'
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def calculate_pip_value(
    symbol: str,
    lot_size: float = 1.0,
) -> float:
    """
    Calculate pip value for a trading symbol.

    Args:
        symbol: Trading symbol
        lot_size: Lot size

    Returns:
        Pip value in account currency

    Example:
        >>> calculate_pip_value("EURUSD", 1.0)
        10.0
    """
    # Simplified pip value calculation
    # For most forex pairs: 1 pip = $10 per standard lot
    # This should be refined based on actual account currency
    standard_pip_value = 10.0

    if "JPY" in symbol:
        # JPY pairs have different pip calculation
        standard_pip_value = 1000.0

    return standard_pip_value * lot_size


def calculate_risk_reward(
    entry: float,
    stop_loss: float,
    take_profit: float,
) -> Optional[float]:
    """
    Calculate risk-reward ratio.

    Args:
        entry: Entry price
        stop_loss: Stop loss price
        take_profit: Take profit price

    Returns:
        Risk-reward ratio or None if invalid

    Example:
        >>> calculate_risk_reward(1.1000, 1.0950, 1.1100)
        2.0
    """
    try:
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)

        if risk == 0:
            logger.warning("Invalid risk calculation: risk is zero")
            return None

        return round(reward / risk, 2)
    except Exception as e:
        logger.error(f"Risk-reward calculation error: {e}")
        return None
