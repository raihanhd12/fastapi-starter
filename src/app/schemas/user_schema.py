from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema dengan common attributes"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, regex="^[a-zA-Z0-9_-]+$")
    full_name: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    """Schema untuk create user baru"""

    password: str = Field(..., min_length=8, max_length=100)

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class UserUpdate(BaseModel):
    """Schema untuk update user"""

    email: Optional[EmailStr] = None
    username: Optional[str] = Field(
        None, min_length=3, max_length=100, regex="^[a-zA-Z0-9_-]+$"
    )
    full_name: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema untuk user response (public info)"""

    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Schema untuk public user profile"""

    id: int
    username: str
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserInternalResponse(UserResponse):
    """Schema untuk internal user response (dengan sensitive info)"""

    is_superuser: bool
    last_login: Optional[datetime]


# Auth related schemas
class LoginRequest(BaseModel):
    """Schema untuk login request"""

    username: str = Field(..., description="Username or email")
    password: str = Field(..., min_length=1)


class Token(BaseModel):
    """Schema untuk JWT token response"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    """Schema untuk token payload data"""

    username: Optional[str] = None
    user_id: Optional[int] = None


class PasswordReset(BaseModel):
    """Schema untuk password reset"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema untuk confirm password reset"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v


class ChangePassword(BaseModel):
    """Schema untuk change password"""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v
