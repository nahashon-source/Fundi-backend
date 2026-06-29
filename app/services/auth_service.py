"""
Auth business logic: registration, login, token issuance.
This is where rules live (e.g. "email must be unique", "password must
match") -- the repository only fetches/saves rows, it doesn't decide anything.
"""
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.exceptions import ConflictException, UnauthorizedException
from app.models.customer_profile import CustomerProfile
from app.models.fundi_profile import FundiProfile
from app.models.user import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, payload: RegisterRequest) -> TokenResponse:
        """Creates a new user + matching profile row, then returns tokens for immediate login."""
        existing = self.user_repo.get_by_email(payload.email)
        if existing:
            raise ConflictException("An account with this email already exists.")

        user = self.user_repo.create(
            email=payload.email,
            phone=payload.phone,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )

        # Create the role-specific profile row. Business rule: every user
        # gets exactly one profile matching their role at registration time.
        if payload.role == UserRole.CUSTOMER:
            profile = CustomerProfile(user_id=user.id, full_name=payload.full_name)
            self.db.add(profile)
        elif payload.role == UserRole.FUNDI:
            profile = FundiProfile(user_id=user.id, business_name=payload.full_name)
            self.db.add(profile)
        # ADMIN role: no profile table -- admins are managed directly via the User table.

        self.db.commit()

        return self._issue_tokens(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        """Verifies credentials and issues a fresh token pair."""
        user = self.user_repo.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Incorrect email or password.")
        if not user.is_active:
            raise UnauthorizedException("This account has been deactivated.")

        return self._issue_tokens(user)

    def _issue_tokens(self, user) -> TokenResponse:
        claims = {"sub": str(user.id), "role": user.role.value}
        return TokenResponse(
            access_token=create_access_token(claims),
            refresh_token=create_refresh_token(claims),
        )