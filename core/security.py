# core/security.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from configs.settings import settings
from database.session import get_db
from database.models.user import User, UserRole
from utils.exceptions import AuthenticationError, AuthorizationError

# Use pbkdf2_sha256 instead of bcrypt to avoid version issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError:
        raise AuthenticationError("Invalid or expired token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if not user_id:
        raise AuthenticationError("Invalid token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    return user

def require_role(required_role: UserRole):
    def role_checker(user: User = Depends(get_current_user)):
        if user.role != required_role and user.role != UserRole.ADMIN:
            raise AuthorizationError("Insufficient permissions")
        return user
    return role_checker

def require_admin(user: User = Depends(require_role(UserRole.ADMIN))):
    return user