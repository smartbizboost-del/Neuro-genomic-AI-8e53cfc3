"""
Authentication routes for user login and registration
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta

from src.api.middleware.auth import create_access_token, verify_token, get_current_user, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])

# Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "researcher"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    created_at: datetime

# Mock user database (replace with real DB)
MOCK_USERS_DB = {}

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserRegister):
    """Register a new user"""
    if user_data.email in MOCK_USERS_DB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_id = f"user_{len(MOCK_USERS_DB) + 1}"
    hashed_password = get_password_hash(user_data.password)
    
    role = "admin" if len(MOCK_USERS_DB) == 0 else user_data.role
    
    MOCK_USERS_DB[user_data.email] = {
        "id": user_id,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": role,
        "hashed_password": hashed_password,
        "created_at": datetime.now(),
        "status": "active"  # Active by default
    }
    
    return UserResponse(
        id=user_id,
        email=user_data.email,
        full_name=user_data.full_name,
        role=role,
        created_at=datetime.now()
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Login and receive access token"""
    user = MOCK_USERS_DB.get(login_data.email)
    
    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.get("status") == "suspended":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended. Contact admin."
        )
    
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"], "user_id": user["id"]}
    )
    
    return TokenResponse(
        access_token=access_token,
        expires_in=3600 * 24  # 24 hours
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(
        id=current_user["user_id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        role=current_user["role"],
        created_at=datetime.now()
    )