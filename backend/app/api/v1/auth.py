"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.auth import create_access_token
from app.db.session import get_db

router = APIRouter()


@router.post("/auth/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT token."""
    
    # TODO: Implement proper user authentication
    # For now, accept any username/password (development only)
    if form_data.username and form_data.password:
        access_token = create_access_token(data={"sub": form_data.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.post("/auth/verify")
async def verify_token(current_user: dict = Depends(get_current_user)):
    """Verify current token is valid."""
    return {"valid": True, "user": current_user}
