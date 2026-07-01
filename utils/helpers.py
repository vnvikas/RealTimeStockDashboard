"""
Helper utility functions.
"""

import os
import secrets
import hashlib
import re
from datetime import datetime, timedelta
from flask import request, current_app
from werkzeug.utils import secure_filename
from PIL import Image


def get_client_ip():
    """
    Get client IP address from request.
    
    Returns:
        str: Client IP address
    """
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or '0.0.0.0'


def get_user_agent():
    """
    Get user agent string from request.
    
    Returns:
        str: User agent string
    """
    return request.headers.get('User-Agent', 'Unknown')


def generate_token(length=32):
    """
    Generate a secure random token.
    
    Args:
        length: Token length
        
    Returns:
        str: Generated token
    """
    return secrets.token_urlsafe(length)


def hash_string(value):
    """
    Hash a string using SHA-256.
    
    Args:
        value: String to hash
        
    Returns:
        str: Hashed string
    """
    return hashlib.sha256(value.encode()).hexdigest()


def save_profile_picture(file, user_id):
    """
    Save profile picture to disk.
    
    Args:
        file: File object
        user_id: User ID
        
    Returns:
        str: Saved filename or None
    """
    if not file or not file.filename:
        return None
    
    # Check file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
        return None
    
    # Generate secure filename
    filename = f'user_{user_id}_{datetime.utcnow().strftime("%Y%m%d%H%M%S")}{ext}'
    filename = secure_filename(filename)
    
    # Ensure upload directory exists
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    # Save file
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    # Optimize image
    try:
        with Image.open(file_path) as img:
            # Resize to max 500x500
            img.thumbnail((500, 500))
            img.save(file_path, quality=85, optimize=True)
    except Exception as e:
        current_app.logger.error(f'Image optimization error: {str(e)}')
    
    return filename


def format_currency(amount, currency='USD'):
    """
    Format amount as currency.
    
    Args:
        amount: Amount to format
        currency: Currency code
        
    Returns:
        str: Formatted currency string
    """
    if amount is None:
        amount = 0
    
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'INR': '₹'
    }
    
    symbol = currency_symbols.get(currency, '$')
    return f'{symbol}{float(amount):,.2f}'


def format_percentage(value):
    """
    Format value as percentage.
    
    Args:
        value: Value to format
        
    Returns:
        str: Formatted percentage string
    """
    if value is None:
        value = 0
    
    return f'{float(value):.2f}%'


def calculate_time_ago(dt):
    """
    Calculate time ago string.
    
    Args:
        dt: Datetime object
        
    Returns:
        str: Time ago string
    """
    if not dt:
        return ''
    
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        return f'{diff.days // 365} year(s) ago'
    elif diff.days > 30:
        return f'{diff.days // 30} month(s) ago'
    elif diff.days > 0:
        return f'{diff.days} day(s) ago'
    elif diff.seconds > 3600:
        return f'{diff.seconds // 3600} hour(s) ago'
    elif diff.seconds > 60:
        return f'{diff.seconds // 60} minute(s) ago'
    else:
        return 'Just now'


def validate_url(url):
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid URL
    """
    if not url:
        return True
    
    pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    return bool(pattern.match(url))


def truncate_text(text, length=100, suffix='...'):
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to add
        
    Returns:
        str: Truncated text
    """
    if not text:
        return ''
    
    if len(text) <= length:
        return text
    
    return text[:length].strip() + suffix


def parse_date(date_string):
    """
    Parse date string in various formats.
    
    Args:
        date_string: Date string
        
    Returns:
        datetime: Parsed datetime or None
    """
    if not date_string:
        return None
    
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%b %d, %Y',
        '%B %d, %Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None


def slugify(text):
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        
    Returns:
        str: Slugified text
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text