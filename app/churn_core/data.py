"""
Data utilities and formatting functions for Streamlit UI.
"""
from typing import Union

def format_inr(value: Union[int, float]) -> str:
    """
    Format currency with Indian grouping (₹12,34,567).
    """
    if not isinstance(value, (int, float)) or value == 0:
        return "₹0"
    
    # Convert to string and handle negative values
    is_negative = value < 0
    value = abs(value)
    
    # Round to nearest integer for display
    s = f"{int(round(value))}"
    
    # Indian number formatting: last 3 digits, then groups of 2
    if len(s) <= 3:
        result = f"₹{s}"
    else:
        last3 = s[-3:]
        rest = s[:-3]
        
        # Group the rest in pairs from right to left
        groups = []
        for i in range(len(rest), 0, -2):
            start = max(i-2, 0)
            groups.append(rest[start:i])
        
        # Reverse to get correct order
        groups.reverse()
        formatted_rest = ",".join(groups)
        
        result = f"₹{formatted_rest},{last3}"
    
    return f"-{result}" if is_negative else result

def format_percent(value: Union[int, float], decimals: int = 1) -> str:
    """
    Format percentage with specified decimal places.
    """
    if not isinstance(value, (int, float)):
        return "0.0%"
    
    return f"{value:.{decimals}f}%"

def format_days(value: Union[int, float]) -> str:
    """
    Format days with appropriate suffix.
    """
    if not isinstance(value, (int, float)):
        return "0 days"
    
    days = int(round(value))
    if days == 1:
        return "1 day"
    else:
        return f"{days} days"

def format_months(value: Union[int, float]) -> str:
    """
    Format months with appropriate suffix.
    """
    if not isinstance(value, (int, float)):
        return "0 mo"
    
    months = round(value, 1)
    return f"{months} mo"

def format_score_as_odds(score: Union[int, float]) -> str:
    """
    Convert 0-1 score to come-back odds percentage.
    """
    if not isinstance(score, (int, float)):
        return "0.0%"
    
    percentage = score * 100
    return f"{percentage:.1f}%"

def safe_get(data: dict, key: str, default=0):
    """
    Safely get value from dictionary with fallback.
    """
    return data.get(key, default) if isinstance(data, dict) else default