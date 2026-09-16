"""Authentication service.

Handles user registration, login, token refresh, and credential generation.
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import User, Admission
from app.security.auth import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, generate_student_id
)
from app.schemas import UserCreate, UserResponse
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AuthService:
    """Authentication and user management service."""

    @staticmethod
    def register_student(
        db: Session,
        user_data: UserCreate,
        admission_year: int,
        branch: str,
        course: str = "B.Tech"
    ) -> dict:
        """Register a new student with automatic credential generation.

        Args:
            db: Database session
            user_data: User creation data
            admission_year: Year of admission
            branch: Student branch (CSE, ECE, etc.)
            course: Course name

        Returns:
            dict: User and admission data with generated credentials

        Raises:
            ValueError: If email already exists or registration fails
        """
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise ValueError(f"User with email {user_data.email} already exists")

            # Create user
            hashed_password = hash_password(user_data.password)
            user = User(
                name=user_data.name,
                email=user_data.email,
                hashed_password=hashed_password,
                role="STUDENT",
                phone=user_data.phone,
                bio=user_data.bio,
                is_active=True
            )
            db.add(user)
            db.flush()  # Get user ID without committing

            # Generate student ID
            # Get the count of admissions for this year and branch
            count = db.query(Admission).filter(
                Admission.admission_year == admission_year,
                Admission.branch == branch
            ).count()
            student_id = generate_student_id(admission_year, branch, count + 1)

            # Create admission record
            admission = Admission(
                user_id=user.id,
                student_id=student_id,
                course=course,
                branch=branch,
                semester=1,
                admission_year=admission_year,
                admission_date=datetime.utcnow(),
                status="ACTIVE"
            )
            user.student_id = student_id
            db.add(admission)
            db.commit()

            logger.info(f"Student registered: {user.email} with ID {student_id}")

            return {
                "user_id": user.id,
                "email": user.email,
                "name": user.name,
                "student_id": student_id,
                "branch": branch,
                "semester": 1,
                "message": "Registration successful. Use your email and password to login."
            }
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Registration integrity error: {e}")
            raise ValueError("Registration failed: Email or student ID already exists")
        except Exception as e:
            db.rollback()
            logger.error(f"Registration error: {e}")
            raise

    @staticmethod
    def authenticate_user(
        db: Session,
        email: str,
        password: str
    ) -> Optional[dict]:
        """Authenticate user and generate tokens.

        Args:
            db: Database session
            email: User email
            password: Plain text password

        Returns:
            dict: Token data if authentication successful, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed login attempt for email: {email}")
            return None

        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {email}")
            return None

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Generate tokens
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            student_id=user.student_id
        )
        refresh_token = create_refresh_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            student_id=user.student_id
        )

        logger.info(f"User authenticated: {email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60
        }

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
