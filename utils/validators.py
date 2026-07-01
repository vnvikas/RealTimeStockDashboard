"""
Validation utility functions.
"""

import re
from datetime import datetime


def validate_email(email):
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid email
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username):
    """
    Validate username format.
    
    Args:
        username: Username to validate
        
    Returns:
        bool: True if valid username
    """
    if not username:
        return False
    
    # Username should be 3-50 characters, alphanumeric and underscore
    pattern = r'^[a-zA-Z0-9_]{3,50}$'
    return bool(re.match(pattern, username))


def validate_password_strength(password):
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        tuple: (is_valid, message)
    """
    if not password:
        return False, 'Password is required.'
    
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long.'
    
    # Check for at least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    
    # Check for at least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'
    
    # Check for at least one digit
    if not re.search(r'[0-9]', password):
        return False, 'Password must contain at least one number.'
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, 'Password must contain at least one special character.'
    
    return True, 'Password is strong.'


def validate_phone_number(phone):
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        bool: True if valid phone number
    """
    if not phone:
        return True  # Phone number is optional
    
    # Basic international phone number validation
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, phone))


def validate_date(date_string):
    """
    Validate date string.
    
    Args:
        date_string: Date string to validate
        
    Returns:
        bool: True if valid date
    """
    if not date_string:
        return False
    
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_positive_number(value):
    """
    Validate that value is a positive number.
    
    Args:
        value: Value to validate
        
    Returns:
        bool: True if positive number
    """
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False


def validate_non_negative_number(value):
    """
    Validate that value is a non-negative number.
    
    Args:
        value: Value to validate
        
    Returns:
        bool: True if non-negative number
    """
    try:
        num = float(value)
        return num >= 0
    except (ValueError, TypeError):
        return False


def validate_url(url):
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid URL
    """
    if not url:
        return True  # URL is optional
    
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    return bool(pattern.match(url))


def validate_stock_symbol(symbol):
    """
    Validate stock symbol format.
    
    Args:
        symbol: Stock symbol to validate
        
    Returns:
        bool: True if valid stock symbol
    """
    if not symbol:
        return False
    
    # Stock symbols are typically 1-5 uppercase letters
    pattern = r'^[A-Z]{1,5}$'
    return bool(re.match(pattern, symbol.upper()))


def validate_quantity(quantity):
    """
    Validate stock quantity.
    
    Args:
        quantity: Quantity to validate
        
    Returns:
        bool: True if valid quantity
    """
    try:
        qty = float(quantity)
        return qty > 0 and qty.is_integer()
    except (ValueError, TypeError):
        return False


def validate_price(price):
    """
    Validate stock price.
    
    Args:
        price: Price to validate
        
    Returns:
        bool: True if valid price
    """
    try:
        p = float(price)
        return p > 0
    except (ValueError, TypeError):
        return False