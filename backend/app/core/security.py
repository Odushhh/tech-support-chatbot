import secrets
from datetime import datetime, timedelta
from typing import Any, Union

from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_403_FORBIDDEN
from pydantic import ValidationError

from backend.app.core.config import settings
from backend.app.utils.helpers import generate_random_string

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Create a new access token
def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# Verify a password against a hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Hash a password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# Decode a JWT token
def decode_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return decoded_token if decoded_token["exp"] >= datetime.utcnow().timestamp() else None
    except jwt.JWTError:
        return None

# Get the current user from the token
async def get_current_user(token: str = Security(oauth2_scheme)):
    try:
        payload = decode_token(token)
        if payload is None:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")
    except (jwt.JWTError, ValidationError):
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")
    
    # Here you would typically fetch the user from your database
    # For this example, we'll just return the user_id
    return {"id": user_id}

# Generate a secure reset token
def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

# Hash a reset token for secure storage
def hash_reset_token(token: str) -> str:
    return pwd_context.hash(token)

# Verify a reset token against a hash
def verify_reset_token(plain_token: str, hashed_token: str) -> bool:
    return pwd_context.verify(plain_token, hashed_token)

# Generate a secure API key
def generate_api_key() -> str:
    return f"sk_{generate_random_string(32)}"

# Hash an API key for secure storage
def hash_api_key(api_key: str) -> str:
    return pwd_context.hash(api_key)

# Verify an API key against a hash
def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    return pwd_context.verify(plain_api_key, hashed_api_key)

# Encrypt sensitive data (placeholder - implement actual encryption)
def encrypt_sensitive_data(data: str) -> str:
    # TODO: Implement actual encryption (e.g., using Fernet)
    return f"encrypted_{data}"

# Decrypt sensitive data (placeholder - implement actual decryption)
def decrypt_sensitive_data(encrypted_data: str) -> str:
    # TODO: Implement actual decryption
    return encrypted_data.replace("encrypted_", "")

# Generate a CSRF token
def generate_csrf_token() -> str:
    return secrets.token_hex(16)

# Sanitize user input to prevent XSS attacks
def sanitize_input(input_string: str) -> str:
    # This is a very basic implementation. Consider using a library like bleach for more comprehensive sanitization
    return input_string.replace("<", "&lt;").replace(">", "&gt;")

# Validate password strength
def validate_password_strength(password: str) -> bool:
    # Check for minimum length
    if len(password) < 8:
        return False
    # Check for at least one uppercase letter, one lowercase letter, one digit, and one special character
    if not any(c.isupper() for c in password):
        return False
    if not any(c.islower() for c in password):
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return False
    return True

# Basic rate limiting function (placeholder - implement actual rate limiting)
def rate_limit(key: str, limit: int, period: int) -> bool:
    # TODO: Implement actual rate limiting (e.g., using Redis)
    return True

# Example usage
if __name__ == "__main__":
    # Password hashing
    password = "mysecurepassword"
    hashed_password = get_password_hash(password)
    print(f"Hashed password: {hashed_password}")
    print(f"Password verification: {verify_password(password, hashed_password)}")

    # Token creation
    token = create_access_token("user123")
    print(f"Access token: {token}")

    # Token decoding
    decoded = decode_token(token)
    print(f"Decoded token: {decoded}")

    # Reset token
    reset_token = generate_reset_token()
    hashed_reset_token = hash_reset_token(reset_token)
    print(f"Reset token: {reset_token}")
    print(f"Reset token verification: {verify_reset_token(reset_token, hashed_reset_token)}")

    # API key
    api_key = generate_api_key()
    hashed_api_key = hash_api_key(api_key)
    print(f"API key: {api_key}")
    print(f"API key verification: {verify_api_key(api_key, hashed_api_key)}")

    # Password strength validation
    strong_password = "StrongP@ssw0rd"
    weak_password = "weakpass"
    print(f"Strong password validation: {validate_password_strength(strong_password)}")
    print(f"Weak password validation: {validate_password_strength(weak_password)}")

    # Input sanitization
    malicious_input = "<script>alert('XSS');</script>"
    sanitized_input = sanitize_input(malicious_input)
    print(f"Sanitized input: {sanitized_input}")

    # CSRF token
    csrf_token = generate_csrf_token()
    print(f"CSRF token: {csrf_token}")

