"""
Custom Jinja2 filters for PDF generation
"""

from datetime import datetime
from typing import Any


def strftime_filter(value: Any, format_string: str = "%Y-%m-%d") -> str:
    """
    Custom Jinja2 filter for date formatting
    
    Args:
        value: Date value (datetime object or string)
        format_string: Format string for strftime
        
    Returns:
        Formatted date string
    """
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            # Try to parse common date formats
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"]:
                try:
                    value = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
            else:
                return value  # Return original string if can't parse
        except:
            return value
    
    if isinstance(value, datetime):
        return value.strftime(format_string)
    
    return str(value)


def currency_filter(value: Any, currency: str = "USD", decimals: int = 2) -> str:
    """
    Custom Jinja2 filter for currency formatting
    
    Args:
        value: Numeric value
        currency: Currency symbol
        decimals: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    if value is None:
        return f"{currency} 0.00"
    
    try:
        num_value = float(value)
        formatted = f"{num_value:,.{decimals}f}"
        return f"{currency} {formatted}"
    except (ValueError, TypeError):
        return f"{currency} 0.00"


def percentage_filter(value: Any, decimals: int = 1) -> str:
    """
    Custom Jinja2 filter for percentage formatting
    
    Args:
        value: Numeric value (0-100 or 0-1)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if value is None:
        return "0%"
    
    try:
        num_value = float(value)
        # If value is between 0 and 1, multiply by 100
        if 0 <= num_value <= 1:
            num_value *= 100
        
        formatted = f"{num_value:.{decimals}f}"
        return f"{formatted}%"
    except (ValueError, TypeError):
        return "0%"


def safe_html_filter(value: Any) -> str:
    """
    Custom Jinja2 filter to mark HTML as safe
    
    Args:
        value: HTML string
        
    Returns:
        Safe HTML string
    """
    if value is None:
        return ""
    
    return str(value)


# Dictionary of all custom filters
CUSTOM_FILTERS = {
    'strftime': strftime_filter,
    'currency': currency_filter,
    'percentage': percentage_filter,
    'safe_html': safe_html_filter,
}
