# -*- coding: utf-8 -*-
"""
Security utilities for authentication and encryption
"""
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.config import get_settings

# JWT settings
settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Encryption key for Facebook tokens (derived from SECRET_KEY)
def _get_encryption_key() -> bytes:
    """Generate encryption key from SECRET_KEY"""
    # Use first 32 bytes of SECRET_KEY hash as key
    key_hash = hashlib.sha256(SECRET_KEY.encode()).digest()
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_hash)


def _prehash_password(password: str) -> bytes:
    """
    Pre-hash password with SHA-256 to handle passwords longer than 72 bytes.
    Bcrypt has a 72-byte limit, so we hash longer passwords first.
    """
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    
    # If password is longer than 72 bytes, pre-hash it
    if len(password_bytes) > 72:
        # Hash with SHA-256 to get fixed 32-byte output
        sha256_hash = hashlib.sha256(password_bytes).digest()
        # Return as bytes (32 bytes, well under 72-byte limit)
        return sha256_hash
    else:
        # Return original password bytes if under limit
        return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        # Pre-hash if necessary
        password_bytes = _prehash_password(plain_password)
        
        # Verify using bcrypt
        # hashed_password is stored as string, need to encode it
        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode('utf-8')
        else:
            hashed_password_bytes = hashed_password
            
        return bcrypt.checkpw(password_bytes, hashed_password_bytes)
    except Exception as e:
        # Fallback: try with original password (for backward compatibility)
        try:
            password_bytes = plain_password.encode('utf-8')
            if isinstance(hashed_password, str):
                hashed_password_bytes = hashed_password.encode('utf-8')
            else:
                hashed_password_bytes = hashed_password
            return bcrypt.checkpw(password_bytes, hashed_password_bytes)
        except:
            return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    # Pre-hash if necessary to handle passwords longer than 72 bytes
    password_bytes = _prehash_password(password)
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return as string
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT access token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(db: Session, token: str) -> Optional[User]:
    """Get current user from token"""
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    username: str = payload.get("sub")
    if username is None:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user


def encrypt_token(token: str) -> str:
    """Encrypt Facebook token for secure storage"""
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(token.encode())
        return encrypted.decode()
    except Exception as e:
        raise ValueError(f"Error encrypting token: {e}")


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt Facebook token"""
    try:
        key = _get_encryption_key()
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted_token.encode())
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Error decrypting token: {e}")
