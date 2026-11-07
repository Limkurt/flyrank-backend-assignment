from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from fastapi.security import OAuth2PasswordBearer
from services import auth_service
from services.auth_service import InvalidAuthError
from exceptions import bad_request, invalid_login

router = APIRouter(tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

class AuthRequest(BaseModel):
  email: str
  password: str

class AuthResponse(BaseModel):
  user: AuthRequest
  access_token: str
  refresh_token: str


@router.post("/auth/signup", status_code=201)
def signup(data: AuthRequest):
  try:
    return auth_service.signup(data.email, data.password)
  except InvalidAuthError as e:
    raise bad_request(str(e))

@router.post("/auth/login", status_code=200)
def login(data: AuthRequest):
  try:
    return auth_service.login(data.email, data.password)
  except InvalidAuthError as e:
    raise invalid_login(str(e))

@router.get("/public/info")
def info():
  return {"message": "Welcome stranger! This info is public."}

@router.get("/protected/profile")
async def read_profile(token: Annotated[str, Depends(oauth2_scheme)]):
  if not token or not token.strip():
    raise invalid_login("Access token required")

  return token