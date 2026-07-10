# api/routers/auth.py
"""Authentication endpoints: register and login."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from database.session import get_db
from services.auth_service import AuthService
from schemas.auth import RegisterRequest, UserResponse, Token

router = APIRouter()
auth_service = AuthService()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """OAuth2 login endpoint – returns access token."""
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token = auth_service.create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    user = auth_service.register_user(db, payload)
    # Use model_validate for Pydantic v2 (instead of from_orm)
    return UserResponse.model_validate(user)