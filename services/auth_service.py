from database import supabase

# --------------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------------

class InvalidAuthError(Exception):
  pass

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

def verify_user(token):
  try:
    response = supabase.auth.get_user(token)
    user = response.user

    return {
      "id": user.id,
      "email": user.email,
      "created_at": user.created_at
    }

  except:
    raise InvalidAuthError("Invalid or expired token.")