from fastapi import APIRouter, Depends, Request, status

from backend.models.database import User
from backend.schemas.auth import RefreshTokenRequest, TokenPair, UserCreate, UserLogin, UserProfile
from backend.schemas.common import MessageResponse
from backend.services.auth_service import AuthService, get_auth_service, get_current_user, token_from_request


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, service: AuthService = Depends(get_auth_service)) -> User:
    return service.register(payload)


@router.post("/login", response_model=TokenPair)
async def login(payload: UserLogin, service: AuthService = Depends(get_auth_service)) -> TokenPair:
    return service.login(payload)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshTokenRequest, service: AuthService = Depends(get_auth_service)) -> TokenPair:
    return service.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, service: AuthService = Depends(get_auth_service)) -> MessageResponse:
    token = token_from_request(request)
    if token:
        service.logout(token)
    return MessageResponse(message="Logged out successfully")


@router.get("/profile", response_model=UserProfile)
async def profile(current_user: User = Depends(get_current_user)) -> User:
    return current_user
