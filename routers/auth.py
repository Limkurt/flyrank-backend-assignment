from typing import Annotated
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from services import auth_service
from services.auth_service import InvalidAuthError
from exceptions import bad_request, invalid_login

router = APIRouter(tags=["Authentication"])

class AuthRequest(BaseModel):
  email: str
  password: str

class User(BaseModel):
  id: str
  email: str
  created_at: str


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
def signup(data: AuthRequest):
  try:
    return auth_service.signup(data.email, data.password)
  except InvalidAuthError as e:
    raise bad_request(str(e))

@router.post("/auth/login", status_code=status.HTTP_200_OK)
def login(data: AuthRequest):
  try:
    return auth_service.login(data.email, data.password)
  except InvalidAuthError as e:
    raise invalid_login(str(e))

@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(current_user: Annotated[User, Depends(auth_service.get_current_user)]):
  return auth_service.logout()

@router.get("/public/info")
def info():
  return {"message": "Welcome stranger! This info is public."}

@router.get("/protected/profile")
async def read_profile(current_user: Annotated[User, Depends(auth_service.get_current_user)]):
  return {
    "id": current_user.id,
    "email": current_user.email,
    "created_at": current_user.created_at
  }

@router.get("/protected/dashboard")
async def get_dashboard(current_user: Annotated[User, Depends(auth_service.get_current_user)]):
  return current_user