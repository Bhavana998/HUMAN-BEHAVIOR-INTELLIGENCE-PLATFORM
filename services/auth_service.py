# services/auth_service.py
from typing import Optional
from sqlalchemy.orm import Session
from datetime import timedelta

from core.security import verify_password, get_password_hash, create_access_token
from repositories.user_repository import UserRepository
from schemas.auth import RegisterRequest
from database.models.user import User


class AuthService:
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        repo = UserRepository(db)
        user = repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, user_id: str) -> str:
        return create_access_token({"sub": user_id})

    def create_refresh_token(self, user_id: str) -> str:
        from configs.settings import settings
        return create_access_token(
            {"sub": user_id},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

    def register_user(self, db: Session, payload: RegisterRequest) -> User:
        repo = UserRepository(db)
        existing = repo.get_by_email(payload.email)
        if existing:
            raise ValueError("Email already registered")
        hashed = get_password_hash(payload.password)
        user = User(
            email=payload.email,
            hashed_password=hashed,
            full_name=payload.full_name,
            role=payload.role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user