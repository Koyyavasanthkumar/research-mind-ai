from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.config.settings import settings
from backend.database.session import get_db
from backend.models.database import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth import TokenPair, UserCreate, UserLogin


password_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated=["bcrypt"],
    pbkdf2_sha256__rounds=390000,
)
bearer_scheme = HTTPBearer(auto_error=False)
revoked_tokens: set[str] = set()
DEMO_USER_EMAIL = "demo@researchmind.example.com"


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserCreate) -> User:
        if self.users.get_by_email(payload.email):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")
        return self.users.create(payload.email, payload.full_name, self.hash_password(payload.password))

    def login(self, payload: UserLogin) -> TokenPair:
        user = self.users.get_by_email(payload.email)
        if not user or not self.verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")
        return TokenPair(
            access_token=self.create_token({"sub": str(user.id), "type": "access"}, minutes=settings.access_token_expire_minutes),
            refresh_token=self.create_token({"sub": str(user.id), "type": "refresh"}, days=settings.refresh_token_expire_days),
        )

    def refresh(self, refresh_token: str) -> TokenPair:
        payload = self.decode_token(refresh_token, expected_type="refresh")
        user = self.users.get(int(payload["sub"]))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        revoked_tokens.add(refresh_token)
        return TokenPair(
            access_token=self.create_token({"sub": str(user.id), "type": "access"}, minutes=settings.access_token_expire_minutes),
            refresh_token=self.create_token({"sub": str(user.id), "type": "refresh"}, days=settings.refresh_token_expire_days),
        )

    def logout(self, token: str) -> None:
        revoked_tokens.add(token)

    def hash_password(self, password: str) -> str:
        return password_context.hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        try:
            return password_context.verify(plain, hashed)
        except ValueError:
            return False

    def create_token(self, payload: dict[str, Any], minutes: int | None = None, days: int | None = None) -> str:
        expires = datetime.utcnow() + (timedelta(days=days) if days else timedelta(minutes=minutes or 15))
        data = payload.copy()
        data.update({"exp": expires, "iat": datetime.utcnow()})
        return jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    def decode_token(self, token: str, expected_type: str = "access") -> dict[str, Any]:
        if token in revoked_tokens:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token") from exc
        if payload.get("type") != expected_type:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        return payload


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    service = AuthService(db)
    if credentials is None:
        user = service.users.get_by_email(DEMO_USER_EMAIL)
        if user:
            return user
        return service.users.create(
            DEMO_USER_EMAIL,
            "ResearchMind Demo User",
            service.hash_password("local-demo-password"),
        )
    payload = service.decode_token(credentials.credentials, expected_type="access")
    user = service.users.get(int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or disabled")
    return user


def token_from_request(request: Request) -> str | None:
    authorization = request.headers.get("Authorization", "")
    if authorization.lower().startswith("bearer "):
        return authorization.split(" ", 1)[1]
    return None
