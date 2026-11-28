# OIDC Authentication with Keycloak
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class OIDCSettings(BaseModel):
    """OIDC/Keycloak configuration settings."""

    enabled: bool = False
    authority: str = ""  # Keycloak server URL (e.g., http://localhost:8080/realms/tensor-hub)
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""  # Frontend callback URL
    scopes: str = "openid profile email roles"

    @validator("authority")
    def _must_have_scheme(cls, v: str) -> str:
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Authority must include http:// or https://")
        return v

    @validator("redirect_uri")
    def _redirect_must_have_scheme(cls, v: str) -> str:
        if v and not v.startswith(("http://", "https://")):
            raise ValueError("Redirect URI must include http:// or https://")
        return v


class Token(BaseModel):
    """JWT token response model."""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    """Parsed Keycloak user info."""

    sub: str  # Keycloak user ID
    email: Optional[str] = None
    name: Optional[str] = None
    preferred_username: Optional[str] = None
    roles: list[str] = []


class OIDCSession(BaseModel):
    """User session stored in HttpOnly cookie value."""

    user_id: str
    email: Optional[str] = None
    roles: list[str] = []
    authenticated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_cookie_value(self) -> str:
        """Serialize session for HttpOnly cookie."""
        import json

        data = {
            "user_id": self.user_id,
            "email": self.email,
            "roles": self.roles,
            "authenticated_at": self.authenticated_at.isoformat(),
        }
        return json.dumps(data)

    @classmethod
    def from_cookie_value(cls, value: str) -> OIDCSession:
        """Deserialize session from HttpOnly cookie."""
        import json

        data = json.loads(value)
        return cls(
            user_id=data["user_id"],
            email=data.get("email"),
            roles=data.get("roles", []),
            authenticated_at=datetime.fromisoformat(data["authenticated_at"]),
        )


# OIDC Auth flow helpers
def _build_auth_url(settings: OIDCSettings, state: str, code_verifier: str) -> str:
    """Build Keycloak authorization PKCE URL."""
    from urllib.parse import quote_plus

    params = {
        "client_id": settings.client_id,
        "redirect_uri": settings.redirect_uri,
        "response_type": "code",
        "scope": settings.scopes,
        "state": state,
        "code_challenge": code_verifier,
        "code_challenge_method": "S256",
    }
    base = settings.authority.rstrip("/") + "/protocol/openid-connect/auth"
    qs = "&".join(f"{k}={quote_plus(v)}" for k, v in params.items())
    return f"{base}?{qs}"


def _token_url(settings: OIDCSettings) -> str:
    """Keycloak token endpoint."""
    return settings.authority.rstrip("/") + "/protocol/openid-connect/token"


def _revocation_url(settings: OIDCSettings) -> str:
    """Keycloak token revocation/logout endpoint."""
    return settings.authority.rstrip("/") + "/protocol/openid-connect/logout"

def generate_code_challenge(code_verifier: str, method: str = "S256") -> str:
    """Generate PKCE code challenge from code verifier.

    Args:
        code_verifier: The random string used for PKCE.
        method: Hash method, either "S256" or "plain".

    Returns:
        base64url-encoded code challenge string.

    Raises:
        ValueError: If method is not supported.
    """
    import base64
    import hashlib

    if method == "plain":
        return code_verifier
    elif method == "S256":
        digest = hashlib.sha256(code_verifier.encode()).digest()
        challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return challenge
    else:
        raise ValueError(f"Unsupported code challenge method: {method}. Use 'S256' or 'plain'")



__all__ = [
    "OIDCSettings",
    "Token",
    "UserInfo",
    "OIDCSession",
    "_build_auth_url",
    "_token_url",
    "_revocation_url",
    "generate_code_challenge",
]
