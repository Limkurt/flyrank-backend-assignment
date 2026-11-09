from functools import lru_cache
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field

from exceptions import AuthenticationError
from services.auth_service import AuthService

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)


# ---- schemas -----------------------------------------------------------
class Credentials(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class SignupResponse(BaseModel):
    id: str
    email: str | None
    access_token: str | None
    message: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user_id: str
    email: str | None


class MessageResponse(BaseModel):
    message: str


class ProfileResponse(BaseModel):
    id: str
    email: str | None
    created_at: str | None


# ---- dependencies ------------------------------------------------------
@lru_cache(maxsize=1)
def get_auth_service() -> AuthService:
    return AuthService.from_env()


def get_access_token(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
) -> str:
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing bearer token")
    return credentials.credentials


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
TokenDep = Annotated[str, Depends(get_access_token)]


# ---- auth endpoints ----------------------------------------------------
@router.post(
    "/auth/signup",
    response_model=SignupResponse,
    status_code=201,
    tags=["auth"],
    summary="Create a user",
)
def signup(payload: Credentials, auth: AuthServiceDep) -> SignupResponse:
    result = auth.sign_up(payload.email, payload.password)
    return SignupResponse(**result)


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    tags=["auth"],
    summary="Login a user",
)
def login(payload: Credentials, auth: AuthServiceDep) -> TokenResponse:
    session = auth.sign_in(payload.email, payload.password)
    user: dict[str, Any] = session.get("user") or {}
    return TokenResponse(
        access_token=session.get("access_token", ""),
        refresh_token=session.get("refresh_token", ""),
        token_type=session.get("token_type", "bearer"),
        expires_in=int(session.get("expires_in", 0)),
        user_id=str(user.get("id", "")),
        email=user.get("email"),
    )


@router.post(
    "/auth/logout",
    response_model=MessageResponse,
    tags=["auth"],
    summary="Logout the user",
)
def logout(token: TokenDep, auth: AuthServiceDep) -> MessageResponse:
    auth.sign_out(token)
    return MessageResponse(message="Logged out")


# ---- public / protected ------------------------------------------------
@router.get("/public/info", tags=["public"], summary="Public API info")
def public_info() -> dict[str, Any]:
    return {
        "name": "CRUD API",
        "version": "1.0.0",
        "description": "RESTful CRUD demo with FastAPI, Postgres and Supabase Auth",
        "docs": "/docs",
        "auth": "Supabase (Bearer JWT)",
    }


@router.get(
    "/protected/profile",
    response_model=ProfileResponse,
    tags=["protected"],
    summary="Display user id, email, created at",
)
def profile(token: TokenDep, auth: AuthServiceDep) -> ProfileResponse:
    user = auth.get_user(token)
    return ProfileResponse(
        id=str(user.get("id", "")),
        email=user.get("email"),
        created_at=user.get("created_at"),
    )


@router.get(
    "/protected/dashboard",
    tags=["protected"],
    summary="Display all user info",
)
def dashboard(token: TokenDep, auth: AuthServiceDep) -> dict[str, Any]:
    return auth.get_user(token)
