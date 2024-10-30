import re
import html
import unicodedata
import logging
from typing import List, Dict, Any, Callable
from datetime import datetime, timedelta
from fastapi import HTTPException
import jwt
from passlib.context import CryptContext
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing HTML tags and normalizing whitespace.
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    # Convert to lowercase
    text = text.lower()
    return text

def sanitize_html(text: str) -> str:
    """
    Sanitize HTML text by escaping special characters.
    """
    return html.escape(text)

def format_code_snippet(code: str) -> str:
    """
    Format a code snippet for display, including syntax highlighting placeholders.
    """
    # This is a placeholder. In a real-world scenario, you might use a syntax highlighting library.
    return f"```\n{code}\n```"

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length, appending an ellipsis if truncated.
    """
    return text[:max_length] + '...' if len(text) > max_length else text

def normalize_text(text: str) -> str:
    """
    Normalize Unicode text by converting to lowercase and removing diacritics.
    """
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower())
                   if unicodedata.category(c) != 'Mn')

def extract_urls(text: str) -> List[str]:
    """
    Extract URLs from a given text.
    """
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return url_pattern.findall(text)

def is_valid_email(email: str) -> bool:
    """
    Check if a given string is a valid email address.
    """
    email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    return bool(email_pattern.match(email))

def generate_password_hash(password: str) -> str:
    """
    Generate a hash for the given password.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT access token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"Error decoding access token: {str(e)}")
        return {}

def parse_date(date_string: str) -> datetime:
    """
    Parse a date string into a datetime object.
    """
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        logger.error(f"Invalid date format: {date_string}")
        return None

def format_date(date: datetime) -> str:
    """
    Format a datetime object into a string.
    """
    return date.strftime("%Y-%m-%d %H:%M:%S")

def calculate_time_difference(start_time: datetime, end_time: datetime) -> str:
    """
    Calculate and format the time difference between two datetime objects.
    """
    diff = end_time - start_time
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m {seconds}s"

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '_') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of a specified size.
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def remove_duplicates(lst: List[Any]) -> List[Any]:
    """
    Remove duplicates from a list while preserving order.
    """
    return list(dict.fromkeys(lst))

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning a default value if the denominator is zero.
    """
    return numerator / denominator if denominator != 0 else default

def format_number(number: float, decimal_places: int = 2) -> str:
    """
    Format a number with thousands separators and a specified number of decimal places.
    """
    return f"{number:,.{decimal_places}f}"

def is_valid_url(url: str) -> bool:
    """
    Check if a given string is a valid URL.
    """
    url_pattern = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))

def escape_markdown(text: str) -> str:
    """
    Escape special characters in text for Markdown formatting.
    """
    escape_chars = r'\*_{}[]()#+-.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

def generate_random_string(length: int = 10) -> str:
    """
    Generate a random string of a specified length.
    """
    import random
    import string
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def rate_limit(max_calls: int, time_frame: int) -> Callable:
    """
    Decorator to rate limit a function.
    """
    import time
    from functools import wraps

    def decorator(func):
        last_reset = time.time()
        num_calls = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_reset, num_calls
            if time.time() - last_reset > time_frame:
                last_reset = time.time()
                num_calls = 0
            if num_calls < max_calls:
                num_calls += 1
                return func(*args, **kwargs)
            else:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

        return wrapper

    return decorator

def log_request(query: str):
    """
    Log the incoming request.
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Incoming request: {query}")


logger.info("Helpers module loaded successfully")

