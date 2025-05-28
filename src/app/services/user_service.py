from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime

from src.database.factories.user_factory import User
from src.app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,
)
from src.database.session import get_db

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """
    User Service - Semua business logic untuk User ada disini
    Controller cuma call methods dari service ini
    """

    # =============== Password Utilities ===============
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password dengan bcrypt"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)

    # =============== User Queries ===============
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        with get_db() as db:
            return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address"""
        with get_db() as db:
            return db.query(User).filter(User.email == email.lower()).first()

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        with get_db() as db:
            return db.query(User).filter(User.username == username.lower()).first()

    @staticmethod
    def get_user_by_username_or_email(identifier: str) -> Optional[User]:
        """Get user by username or email (untuk login)"""
        with get_db() as db:
            return (
                db.query(User)
                .filter(
                    (User.username == identifier.lower())
                    | (User.email == identifier.lower())
                )
                .first()
            )

    # =============== User CRUD Operations ===============
    @staticmethod
    def create_user(user_data: UserCreate) -> User:
        """
        Create new user
        Logic: Hash password, check duplicates, create user
        """
        with get_db() as db:
            # Check if email already exists
            if UserService.get_user_by_email(user_data.email):
                raise ValueError("Email already registered")

            # Check if username already exists
            if UserService.get_user_by_username(user_data.username):
                raise ValueError("Username already taken")

            # Hash password
            hashed_password = UserService.hash_password(user_data.password)

            # Create user object
            db_user = User(
                email=user_data.email.lower(),
                username=user_data.username.lower(),
                password=hashed_password,
                full_name=user_data.full_name,
                bio=user_data.bio,
                avatar_url=user_data.avatar_url,
                is_active=True,
                is_verified=False,
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            return db_user

    @staticmethod
    def update_user(user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update existing user"""
        with get_db() as db:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return None

            # Check for email conflicts
            if user_data.email and user_data.email.lower() != db_user.email:
                existing_user = UserService.get_user_by_email(user_data.email)
                if existing_user and existing_user.id != user_id:
                    raise ValueError("Email already registered by another user")

            # Check for username conflicts
            if user_data.username and user_data.username.lower() != db_user.username:
                existing_user = UserService.get_user_by_username(user_data.username)
                if existing_user and existing_user.id != user_id:
                    raise ValueError("Username already taken by another user")

            # Update fields
            update_data = user_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if field in ["email", "username"] and value:
                    value = value.lower()
                setattr(db_user, field, value)

            db.commit()
            db.refresh(db_user)

            return db_user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete user (soft delete by setting is_active = False)"""
        with get_db() as db:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return False

            # Soft delete
            db_user.is_active = False
            db.commit()

            return True

    @staticmethod
    def hard_delete_user(user_id: int) -> bool:
        """Hard delete user (permanent)"""
        with get_db() as db:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return False

            db.delete(db_user)
            db.commit()

            return True

    # =============== User Lists & Search ===============
    @staticmethod
    def get_users(
        skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
    ) -> List[User]:
        """Get users list dengan filter"""
        with get_db() as db:
            query = db.query(User)

            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_users_paginated(
        skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """Get users with total count for pagination"""
        with get_db() as db:
            query = db.query(User)

            if is_active is not None:
                query = query.filter(User.is_active == is_active)

            total = query.count()
            users = query.offset(skip).limit(limit).all()

            return users, total

    @staticmethod
    def search_users(
        query: str, skip: int = 0, limit: int = 50
    ) -> Tuple[List[User], int]:
        """Search users by username, email, or full_name"""
        with get_db() as db:
            search_filter = f"%{query.lower()}%"

            db_query = (
                db.query(User)
                .filter(
                    (User.username.ilike(search_filter))
                    | (User.email.ilike(search_filter))
                    | (User.full_name.ilike(search_filter))
                )
                .filter(User.is_active == True)
            )

            total = db_query.count()
            users = db_query.offset(skip).limit(limit).all()

            return users, total

    # =============== Authentication Logic ===============
    @staticmethod
    def authenticate_user(identifier: str, password: str) -> Optional[User]:
        """
        Authenticate user dengan username/email dan password
        Logic: Find user, verify password, update last_login
        """
        user = UserService.get_user_by_username_or_email(identifier)

        if not user:
            return None

        if not user.is_active:
            raise ValueError("Account is deactivated")

        if not UserService.verify_password(password, user.password):
            return None

        # Update last login
        with get_db() as db:
            db_user = db.query(User).filter(User.id == user.id).first()
            db_user.last_login = datetime.now()
            db.commit()

        return user

    # =============== User Profile & Public Info ===============
    @staticmethod
    def get_user_profile(user_id: int) -> Optional[UserProfile]:
        """Get public user profile"""
        user = UserService.get_user_by_id(user_id)

        if not user or not user.is_active:
            return None

        return UserProfile(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            created_at=user.created_at,
        )

    # =============== User Status Management ===============
    @staticmethod
    def activate_user(user_id: int) -> bool:
        """Activate user account"""
        with get_db() as db:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return False

            db_user.is_active = True
            db.commit()

            return True

    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """Deactivate user account"""
        with get_db() as db:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return False

            db_user.is_active = False
            db.commit()

            return True

    @staticmethod
    def verify_user(user_id: int) -> bool:
        """Mark user as verified"""
        with get_db() as db:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return False

            db_user.is_verified = True
            db.commit()

            return True

    # =============== Password Management ===============
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> bool:
        """Change user password"""
        with get_db() as db:
            db_user = db.query(User).filter(User.id == user_id).first()

            if not db_user:
                return False

            # Verify current password
            if not UserService.verify_password(current_password, db_user.password):
                raise ValueError("Current password is incorrect")

            # Hash new password
            new_hashed = UserService.hash_password(new_password)
            db_user.password = new_hashed
            db.commit()

            return True

    # =============== Utility Methods ===============
    @staticmethod
    def user_exists(identifier: str) -> bool:
        """Check if user exists by username or email"""
        return UserService.get_user_by_username_or_email(identifier) is not None

    @staticmethod
    def get_user_stats() -> dict:
        """Get user statistics"""
        with get_db() as db:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            verified_users = db.query(User).filter(User.is_verified == True).count()

            return {
                "total_users": total_users,
                "active_users": active_users,
                "verified_users": verified_users,
                "inactive_users": total_users - active_users,
            }
