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

  return response

def login(email: str, password: str):
  clean_email = email.strip().lower()

  response = supabase.auth.sign_in_with_password({
    "email": clean_email,
    "password": password
  })

  return response