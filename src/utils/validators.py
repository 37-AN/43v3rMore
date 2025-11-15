"""Input validation utilities."""

import re
from typing import Optional
from loguru import logger


def validate_symbol(symbol: str) -> bool:
    """
    Validate forex trading symbol format.

    Args:
        symbol: Trading symbol to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_symbol("EURUSD")
        True
        >>> validate_symbol("EUR")
        False
    """
    if not symbol or not isinstance(symbol, str):
        return False

    # Forex pairs: 6 characters (e.g., EURUSD)
    # Metals: 5-6 characters (e.g., XAUUSD, GOLD)
    # Indices: 3-8 characters (e.g., US30, NAS100)
    pattern = r"^[A-Z]{3,8}$"

    is_valid = bool(re.match(pattern, symbol.upper()))

    if not is_valid:
        logger.warning(f"Invalid symbol format: {symbol}")

    return is_valid


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not email or not isinstance(email, str):
        return False

    # RFC 5322 simplified pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    is_valid = bool(re.match(pattern, email))

    if not is_valid:
        logger.warning(f"Invalid email format: {email}")

    return is_valid


def validate_phone(phone: str, country_code: str = "ZA") -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate
        country_code: Country code for validation (default: ZA for South Africa)

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_phone("+27821234567")
        True
        >>> validate_phone("0821234567")
        True
    """
    if not phone or not isinstance(phone, str):
        return False

    # Remove spaces, dashes, and parentheses
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)

    if country_code == "ZA":
        # South African numbers: +27XXXXXXXXX or 0XXXXXXXXX
        pattern = r"^(\+27|0)[6-8][0-9]{8}$"
    else:
        # Generic international format
        pattern = r"^\+?[1-9]\d{1,14}$"

    is_valid = bool(re.match(pattern, cleaned))

    if not is_valid:
        logger.warning(f"Invalid phone format: {phone}")

    return is_valid


def validate_price(price: float) -> bool:
    """
    Validate price value.

    Args:
        price: Price to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_price(1.2345)
        True
        >>> validate_price(-10)
        False
    """
    if not isinstance(price, (int, float)):
        return False

    is_valid = price > 0

    if not is_valid:
        logger.warning(f"Invalid price value: {price}")

    return is_valid


def validate_confidence(confidence: float) -> bool:
    """
    Validate confidence score (0.0 to 1.0).

    Args:
        confidence: Confidence score to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_confidence(0.85)
        True
        >>> validate_confidence(1.5)
        False
    """
    if not isinstance(confidence, (int, float)):
        return False

    is_valid = 0.0 <= confidence <= 1.0

    if not is_valid:
        logger.warning(f"Invalid confidence value: {confidence}")

    return is_valid


def validate_plan(plan: str) -> bool:
    """
    Validate subscription plan name.

    Args:
        plan: Plan name to validate

    Returns:
        True if valid, False otherwise

    Example:
        >>> validate_plan("basic")
        True
        >>> validate_plan("invalid")
        False
    """
    valid_plans = {"basic", "pro", "premium", "bot", "enterprise"}
    is_valid = plan.lower() in valid_plans

    if not is_valid:
        logger.warning(f"Invalid plan: {plan}")

    return is_valid
