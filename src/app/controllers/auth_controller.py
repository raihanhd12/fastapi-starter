from fastapi import Request
from typing import Dict, Any

from src.app.controllers.base_controller import BaseController
from src.app.services.auth_service import AuthService
from src.app.schemas.user_schema import UserCreate, LoginRequest, ChangePassword, PasswordReset, PasswordResetConfirm

class AuthController(BaseController):
    """
    Auth Controller - Handle semua authentication requests
    Semua logic ada di AuthService, controller cuma handle request/response
    """

    @classmethod
    def register(cls, user_data: UserCreate, request: Request = None) -> Dict[str, Any]:
        """Handle user registration request"""
        if request:
            cls.log_request(request, "REGISTER")

        try:
            # Validate required fields
            cls.validate_request_data(user_data, ["email", "username", "password"])

            # Call auth service
            result = AuthService.register_user(user_data)

            return cls.success_response(
                data=result,
                message="User registered successfully",
                status_code=201
            )

        except ValueError as e:
            # Handle validation errors from service
            if "already" in str(e).lower():
                raise cls.error_response(
                    message=str(e),
                    status_code=409,
                    error_code="ALREADY_EXISTS"
                )
            else:
                raise cls.error_response(
                    message=str(e),
                    status_code=422,
                    error_code="VALIDATION_ERROR"
                )
        except Exception as e:
            raise cls.handle_service_error(e, "Registration failed")

    @classmethod
    def login(cls, login_data: LoginRequest, request: Request = None) -> Dict[str, Any]:
        """Handle user login request"""
        if request:
            cls.log_request(request, "LOGIN")

        try:
            # Validate required fields
            cls.validate_request_data(login_data, ["username", "password"])

            # Call auth service
            result = AuthService.login_user(login_data.username, login_data.password)

            return cls.success_response(
                data=result,
                message="Login successful"
            )

        except ValueError as e:
            if "invalid" in str(e).lower():
                raise cls.error_response(
                    message="Invalid credentials",
                    status_code=401,
                    error_code="INVALID_CREDENTIALS"
                )
            elif "deactivated" in str(e).lower():
                raise cls.error_response(
                    message="Account is deactivated",
                    status_code=403,
                    error_code="ACCOUNT_DEACTIVATED"
                )
            else:
                raise cls.error_response(
                    message=str(e),
                    status_code=400,
                    error_code="LOGIN_ERROR"
                )
        except Exception as e:
            raise cls.handle_service_error(e, "Login failed")

    @classmethod
    def refresh_token(cls, refresh_token: str, request: Request = None) -> Dict[str, Any]:
        """Handle token refresh request"""
        if request:
            cls.log_request(request, "REFRESH_TOKEN")

        try:
            result = AuthService.refresh_access_token(refresh_token)

            return cls.success_response(
                data=result,
                message="Token refreshed successfully"
            )

        except ValueError as e:
            raise cls.error_response(
                message=str(e),
                status_code=401,
                error_code="INVALID_REFRESH_TOKEN"
            )
        except Exception as e:
            raise cls.handle_service_error(e, "Token refresh failed")

    @classmethod
    def validate_token(cls, token: str, request: Request = None) -> Dict[str, Any]:
        """Handle token validation request"""
        if request:
            cls.log_request(request, "VALIDATE_TOKEN")

        try:
            result = AuthService.validate_token(token)

            if result["valid"]:
                return cls.success_response(
                    data=result,
                    message="Token is valid"
                )
            else:
                raise cls.error_response(
                    message="Token is invalid",
                    status_code=401,
                    error_code="INVALID_TOKEN",
                    details={"error": result.get("error")}
                )

        except Exception as e:
            raise cls.handle_service_error(e, "Token validation failed")

    @classmethod
    def get_current_user(cls, token: str, request: Request = None) -> Dict[str, Any]:
        """Get current user from token"""
        if request:
            cls.log_request(request, "GET_CURRENT_USER")

        try:
            user = AuthService.get_current_user(token)

            return cls.success_response(
                data={
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                    "bio": user.bio,
                    "avatar_url": user.avatar_url,
                    "is_active": user.is_active,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                },
                message="Current user retrieved successfully"
            )

        except ValueError as e:
            raise cls.error_response(
                message=str(e),
                status_code=401,
                error_code="UNAUTHORIZED"
            )
        except Exception as e:
            raise cls.handle_service_error(e, "Failed to get current user")

    @classmethod
    def change_password(cls, user_id: int, password_data: ChangePassword, request: Request = None) -> Dict[str, Any]:
        """Handle change password request"""
        if request: