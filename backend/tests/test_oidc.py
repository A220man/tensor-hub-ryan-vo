"""OIDC Authentication with Keycloak - unit tests for core models and helpers."""

import json
import pytest

from backend.app.core.oidc import (
    OIDCSettings,
    Token,
    UserInfo,
    OIDCSession,
    _build_auth_url,
    _token_url,
    _revocation_url,
)


class TestOIDCSettings:
    def test_minimal_settings(self):
        """OIDCSettings with minimal required fields."""
        settings = OIDCSettings(
            enabled=True,
            authority="http://localhost:8080/realms/tensor-hub",
            client_id="tensor-hub-client",
            redirect_uri="http://localhost:8000/auth/callback",
        )
        assert settings.enabled is True
        assert settings.authority == "http://localhost:8080/realms/tensor-hub"
        assert settings.client_id == "tensor-hub-client"

    def test_authority_validates_scheme(self):
        """Authority must include http:// or https://."""
        with pytest.raises(ValueError, match="Authority must include"):
            OIDCSettings(enabled=True, authority="localhost:8080")

    def test_redirect_uri_validates_scheme(self):
        """Redirect URI must include scheme."""
        with pytest.raises(ValueError, match="Redirect URI must include"):
            OIDCSettings(
                enabled=True,
                authority="http://localhost:8080/realms/tensor-hub",
                redirect_uri="localhost:8080/callback",
            )

    def test_defaults(self):
        """Test default values."""
        settings = OIDCSettings()
        assert settings.enabled is False
        assert settings.authority == ""
        assert settings.scopes == "openid profile email roles"


class TestToken:
    def test_token_creation(self):
        """Token model basic creation."""
        token = Token(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.",
            expires_in=3600,
        )
        assert token.access_token.startswith("eyJ")
        assert token.expires_in == 3600
        assert token.token_type == "bearer"


class TestUserInfo:
    def test_userinfo_creation(self):
        """UserInfo model with required sub."""
        user = UserInfo(sub="user-123", email="user@example.com", name="Test User")
        assert user.sub == "user-123"
        assert user.email == "user@example.com"
        assert user.name == "Test User"

    def test_userinfo_minimal(self):
        """UserInfo with only sub."""
        user = UserInfo(sub="user-456")
        assert user.sub == "user-456"
        assert user.email is None


class TestOIDCSession:
    def test_session_to_from_cookie(self):
        """Session round-trips through cookie serialization."""
        session = OIDCSession(
            user_id="user-789",
            email="user@example.com",
            roles=["viewer", "operator"],
        )
        cookie_val = session.to_cookie_value()
        restored = OIDCSession.from_cookie_value(cookie_val)
        
        assert restored.user_id == session.user_id
        assert restored.email == session.email
        assert restored.roles == session.roles
        # authenticated_at should be close (within a few seconds)
        assert abs((restored.authenticated_at - session.authenticated_at).total_seconds()) < 10

    def test_session_minimal(self):
        """Session with only user_id."""
        session = OIDCSession(user_id="minimal-user")
        cookie_val = session.to_cookie_value()
        restored = OIDCSession.from_cookie_value(cookie_val)
        assert restored.user_id == "minimal-user"
        assert restored.roles == []
        assert restored.email is None


class TestAuthURLHelpers:
    def test_build_auth_url_structure(self):
        """Authorization URL has expected PKCE parameters."""
        settings = OIDCSettings(
            enabled=True,
            authority="http://localhost:8080/realms/tensor-hub",
            client_id="test-client",
            redirect_uri="http://localhost:8000/auth/callback",
        )
        
        # We can't easily generate a code_verifier here without more setup,
        # but verify the function runs and produces a URL
        url = _build_auth_url(settings, "state-123", "code-verifier-456")
        assert "http://localhost:8080/realms/tensor-hub/protocol/openid-connect/auth" in url
        assert "client_id=test-client" in url
        assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Fcallback" in url
        assert "state=state-123" in url
        assert "code_challenge=code-verifier-456" in url
        assert "code_challenge_method=S256" in url

    def test_token_url(self):
        """Token endpoint URL construction."""
        settings = OIDCSettings(
            enabled=True,
            authority="http://localhost:8080/realms/tensor-hub",
        )
        tu = _token_url(settings)
        assert tu == "http://localhost:8080/realms/tensor-hub/protocol/openid-connect/token"

    def test_revocation_url(self):
        """Revocation/logout endpoint URL construction."""
        settings = OIDCSettings(
            enabled=True,
            authority="http://localhost:8080/realms/tensor-hub",
        )
        ru = _revocation_url(settings)
        assert ru == "http://localhost:8080/realms/tensor-hub/protocol/openid-connect/logout"
