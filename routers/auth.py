from fastapi import APIRouter
from pydantic import BaseModel

from services import auth_service
from services.auth_service import InvalidAuthError
from exceptions import bad_request, invalid_login

router = APIRouter(prefix="/auth", tags=["Authentication"])

class AuthRequest(BaseModel):
  email: str
  password: str

@router.post("/signup", status_code=201)
def signup(data: AuthRequest):
  try:
    return auth_service.signup(data.email, data.password)
  except InvalidAuthError as e:
    raise bad_request(str(e))

@router.post("/login", status_code=200)
def login(data: AuthRequest):
  try:
    return auth_service.login(data.email, data.password)
  except InvalidAuthError as e:
    raise invalid_login(str(e))
