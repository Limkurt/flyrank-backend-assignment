from database import supabase
from fastapi import Depends
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer

# --------------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------------

class InvalidAuthError(Exception):
  pass


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def signup(email: str, password: str) -> dict:
  clean_email = email.strip().lower()

  if clean_email and password.strip().lower():
    response = supabase.auth.sign_up({
        "email": clean_email,
        "password": password
      })
  else:
    raise InvalidAuthError("Bad Request")

  return response.user

def login(email: str, password: str):
  clean_email = email.strip().lower()

  response = supabase.auth.sign_in_with_password({
    "email": clean_email,
    "password": password
  })

  return {
    "access_token": response.session.access_token,
    "refresh_token": response.session.refresh_token
  }

def logout():
  supabase.auth.sign_out()

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
  if not token or not token.strip():
    raise InvalidAuthError("Access token required")
  
  try:
    response = supabase.auth.get_user(token)
    user = response.user

    return user

  except:
    raise InvalidAuthError("Invalid or expired token.")