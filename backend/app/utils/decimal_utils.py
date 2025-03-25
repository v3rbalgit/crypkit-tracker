"""Utility functions for working with decimal values."""

from decimal import Decimal
from typing import Union

# Type alias for values that can be converted to Decimal
DecimalValue = Union[Decimal, float, str, int]


def standardize_decimal(value) -> Decimal:
    """
    Convert a value to Decimal with exact precision.

    Args:
        value: The value to convert (can be Decimal, float, str, or int)

    Returns:
        A Decimal with exact precision
    """
    if isinstance(value, Decimal):
        return value

    try:
        # String conversion to preserve exact values
        return Decimal(str(value))
    except (ValueError, TypeError):
        raise ValueError(f"Cannot convert {value} to Decimal")
