from fastapi import APIRouter, Depends, Header, Request
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from src.app.controllers.auth_controller import AuthController
from src.app.schemas.user_schema import (
    UserCreate,
    LoginRequest,
    ChangePassword,
    PasswordReset,
    PasswordResetConfirm,
)

# OAuth2 scheme for swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)

# Define router
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, request: Request):
    """Register new user"""
    return AuthController.register(user_data, request)


@router.post("/login", response_model=dict)
async def login(login_data: LoginRequest, request: Request):
    """Login user with username/email and password"""
    return AuthController.login(login_data, request)


@router.post("/refresh", response_model=dict)
async def refresh_token(
    request: Request,
    refresh_token: str = Header(..., description="Refresh token in header"),
):
    """Refresh access token using refresh token"""
    return AuthController.refresh_token(refresh_token, request)


@router.post("/validate", response_model=dict)
async def validate_token(request: Request, token: str = Depends(oauth2_scheme)):
    """Validate access token"""
    return AuthController.validate_token(token, request)


@router.get("/me", response_model=dict)
async def get_current_user(request: Request, token: str = Depends(oauth2_scheme)):
    """Get current user information from token"""
    return AuthController.get_current_user(token, request)


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: ChangePassword, request: Request, token: str = Depends(oauth2_scheme)
):
    """Change user password"""
    # Extract user ID from token first
    user_info = AuthController.get_current_user(token, request)
    user_id = user_info["data"]["id"]

    return AuthController.change_password(user_id, password_data, request)


@router.post("/forgot-password", response_model=dict)
async def request_password_reset(reset_data: PasswordReset, request: Request):
    """Request password reset"""
    return AuthController.request_password_reset(reset_data, request)


@router.post("/reset-password", response_model=dict)
async def reset_password(reset_data: PasswordResetConfirm, request: Request):
    """Reset password using reset token"""
    return AuthController.reset_password(reset_data, request)


@router.post("/logout", response_model=dict)
async def logout(request: Request, token: str = Depends(oauth2_scheme)):
    """Logout user"""
    return AuthController.logout(token, request)


@router.get("/token-info", response_model=dict)
async def get_token_info(request: Request, token: str = Depends(oauth2_scheme)):
    """Get token information"""
    return AuthController.get_token_info(token, request)
