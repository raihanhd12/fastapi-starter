from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import secrets

from src.app.services.user_service import UserService
from src.database.factories.user_factory import User
from src.app.schemas.user_schema import UserCreate, UserResponse, Token, TokenData

# Configuration - nanti bisa dipindah ke config file
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthService:
    """
    Auth Service - Semua logic authentication ada disini
    Handle JWT, login, register, token validation, dll
    """

    # =============== JWT Token Management ===============
    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Create refresh token for token renewal"""
        data = {
            "user_id": user_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=7),  # 7 days
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),  # JWT ID untuk invalidation
        }

        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> TokenData:
        """
        Verify JWT token dan return token data
        Raise exception jika token invalid
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check token type
            token_type = payload.get("type", "access")
            if token_type != "access":
                raise ValueError("Invalid token type")

            # Extract user info
            username: str = payload.get("sub")
            user_id: int = payload.get("user_id")

            if username is None and user_id is None:
                raise ValueError("Token missing user identification")

            return TokenData(username=username, user_id=user_id)

        except JWTError as e:
            raise ValueError(f"Token validation failed: {str(e)}")

    @staticmethod
    def get_current_user(token: str) -> User:
        """Get current user from JWT token"""
        token_data = AuthService.verify_token(token)

        # Get user by username or user_id
        if token_data.username:
            user = UserService.get_user_by_username(token_data.username)
        elif token_data.user_id:
            user = UserService.get_user_by_id(token_data.user_id)
        else:
            raise ValueError("Token data incomplete")

        if user is None:
            raise ValueError("User not found")

        if not user.is_active:
            raise ValueError("User account is deactivated")

        return user

    # =============== Authentication Methods ===============
    @staticmethod
    def register_user(user_data: UserCreate) -> Dict[str, Any]:
        """
        Register new user
        Logic: Create user, generate token, return response
        """
        try:
            # Create user via UserService
            user = UserService.create_user(user_data)

            # Generate access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = AuthService.create_access_token(
                data={"sub": user.username, "user_id": user.id, "email": user.email},
                expires_delta=access_token_expires,
            )

            # Generate refresh token
            refresh_token = AuthService.create_refresh_token(user.id)

            # Convert user to response format
            user_response = UserResponse.model_validate(user)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
                "user": user_response,
            }

        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Registration failed: {str(e)}")

    @staticmethod
    def login_user(identifier: str, password: str) -> Dict[str, Any]:
        """
        Login user dengan username/email dan password
        Logic: Authenticate, generate tokens, return response
        """
        try:
            # Authenticate user
            user = UserService.authenticate_user(identifier, password)

            if not user:
                raise ValueError("Invalid username/email or password")

            # Generate access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = AuthService.create_access_token(
                data={"sub": user.username, "user_id": user.id, "email": user.email},
                expires_delta=access_token_expires,
            )

            # Generate refresh token
            refresh_token = AuthService.create_refresh_token(user.id)

            # Convert user to response format
            user_response = UserResponse.model_validate(user)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # seconds
                "user": user_response,
            }

        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Login failed: {str(e)}")

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check token type
            if payload.get("type") != "refresh":
                raise ValueError("Invalid token type")

            user_id = payload.get("user_id")
            if not user_id:
                raise ValueError("Invalid refresh token")

            # Get user
            user = UserService.get_user_by_id(user_id)
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")

            # Generate new access token
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = AuthService.create_access_token(
                data={"sub": user.username, "user_id": user.id, "email": user.email},
                expires_delta=access_token_expires,
            )

            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }

        except JWTError as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Token refresh failed: {str(e)}")

    # =============== Token Validation ===============
    @staticmethod
    def validate_token(token: str) -> Dict[str, Any]:
        """Validate token dan return user info"""
        try:
            user = AuthService.get_current_user(token)

            return {
                "valid": True,
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    # =============== Password Management ===============
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            return UserService.change_password(user_id, current_password, new_password)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            raise ValueError(f"Password change failed: {str(e)}")

    @staticmethod
    def generate_password_reset_token(email: str) -> str:
        """Generate password reset token"""
        user = UserService.get_user_by_email(email)
        if not user:
            raise ValueError("User with this email not found")

        # Generate reset token with short expiry
        data = {
            "user_id": user.id,
            "email": user.email,
            "type": "password_reset",
            "exp": datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
            "iat": datetime.utcnow(),
            "jti": secrets.token_urlsafe(32),
        }

        return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def reset_password_with_token(reset_token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        try:
            # Decode reset token
            payload = jwt.decode(reset_token, SECRET_KEY, algorithms=[ALGORITHM])

            # Check token type
            if payload.get("type") != "password_reset":
                raise ValueError("Invalid token type")

            user_id = payload.get("user_id")
            if not user_id:
                raise ValueError("Invalid reset token")

            # Get user and update password
            user = UserService.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Hash and update password
            hashed_password = UserService.hash_password(new_password)

            with UserService.get_db() as db:
                db_user = db.query(User).filter(User.id == user_id).first()
                db_user.password = hashed_password
                db.commit()

            return True

        except JWTError as e:
            raise ValueError(f"Invalid reset token: {str(e)}")
        except Exception as e:
            raise ValueError(f"Password reset failed: {str(e)}")

    # =============== Utility Methods ===============
    @staticmethod
    def get_token_info(token: str) -> Dict[str, Any]:
        """Get token information without validation"""
        try:
            # Decode without verification to get info
            payload = jwt.decode(token, options={"verify_signature": False})

            return {
                "user_id": payload.get("user_id"),
                "username": payload.get("sub"),
                "email": payload.get("email"),
                "token_type": payload.get("type", "access"),
                "issued_at": datetime.fromtimestamp(payload.get("iat", 0)).isoformat(),
                "expires_at": datetime.fromtimestamp(payload.get("exp", 0)).isoformat(),
            }

        except Exception as e:
            return {"error": f"Unable to decode token: {str(e)}"}

    @staticmethod
    def is_token_expired(token: str) -> bool:
        """Check if token is expired"""
        try:
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return False
        except jwt.ExpiredSignatureError:
            return True
        except Exception:
            return True
