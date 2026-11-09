import os
from typing import Any

import httpx

from exceptions import (
    AuthenticationError,
    AuthRequestError,
    AuthServiceUnavailableError,
)


class AuthService:
    """Thin, stateless wrapper over Supabase Auth (GoTrue) REST API."""

    def __init__(self, supabase_url: str, api_key: str, timeout: float = 10.0) -> None:
        self._client = httpx.Client(
            base_url=f"{supabase_url.rstrip('/')}/auth/v1",
            headers={"apikey": api_key},
            timeout=timeout,
        )

    @classmethod
    def from_env(cls) -> "AuthService":
        url = os.getenv("SUPABASE_URL", "").strip()
        key = os.getenv("SUPABASE_KEY", "").strip()
        if not url or not key:
            raise AuthServiceUnavailableError(
                "Supabase is not configured. Set SUPABASE_URL and SUPABASE_KEY."
            )
        return cls(url, key)

    # ---- helpers -------------------------------------------------------
    def _request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
    ) -> httpx.Response:
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        try:
            return self._client.request(
                method, path, headers=headers, json=json, params=params
            )
        except (httpx.HTTPError, httpx.InvalidURL) as exc:
            raise AuthServiceUnavailableError() from exc

    @staticmethod
    def _body(resp: httpx.Response) -> dict[str, Any]:
        try:
            data = resp.json()
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}

    @classmethod
    def _message(cls, resp: httpx.Response, fallback: str) -> str:
        body = cls._body(resp)
        for key in ("msg", "error_description", "message", "error"):
            value = body.get(key)
            if isinstance(value, str) and value:
                return value
        return fallback

    # ---- operations ----------------------------------------------------
    def sign_up(self, email: str, password: str) -> dict[str, Any]:
        resp = self._request(
            "POST", "/signup", json={"email": email, "password": password}
        )
        if resp.status_code >= 500:
            raise AuthServiceUnavailableError(self._message(resp, "Signup failed"))
        if resp.status_code >= 400:
            raise AuthRequestError(self._message(resp, "Signup failed"))

        body = self._body(resp)
        user: dict[str, Any] = body.get("user", body)
        access_token: str | None = body.get("access_token")
        return {
            "id": str(user.get("id", "")),
            "email": user.get("email"),
            "access_token": access_token,
            "message": (
                "User created."
                if access_token
                else "User created. Check your email to confirm the account."
            ),
        }

    def sign_in(self, email: str, password: str) -> dict[str, Any]:
        resp = self._request(
            "POST",
            "/token",
            params={"grant_type": "password"},
            json={"email": email, "password": password},
        )
        if resp.status_code >= 500:
            raise AuthServiceUnavailableError(self._message(resp, "Login failed"))
        if resp.status_code >= 400:
            raise AuthenticationError(
                self._message(resp, "Invalid login credentials")
            )
        return self._body(resp)

    def get_user(self, token: str) -> dict[str, Any]:
        resp = self._request("GET", "/user", token=token)
        if resp.status_code >= 500:
            raise AuthServiceUnavailableError()
        if resp.status_code >= 400:
            raise AuthenticationError("Invalid or expired token")
        return self._body(resp)

    def sign_out(self, token: str) -> None:
        resp = self._request("POST", "/logout", token=token)
        if resp.status_code >= 500:
            raise AuthServiceUnavailableError()
        if resp.status_code >= 400:
            raise AuthenticationError("Invalid or expired token")
