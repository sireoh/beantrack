"""Discord OAuth2 (authorization code grant) client."""

from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, ValidationError

from app.core.errors import AuthenticationError, UpstreamError

AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"
CURRENT_USER_URL = "https://discord.com/api/users/@me"
SCOPES = "identify"


class DiscordTokens(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_in: int
    token_type: str = "Bearer"
    scope: str = ""


class DiscordUser(BaseModel):
    id: str
    username: str
    global_name: str | None = None
    avatar: str | None = None


class DiscordOAuthClient:
    def __init__(
        self, http: httpx.Client, *, client_id: str, client_secret: str, redirect_uri: str
    ) -> None:
        self._http = http
        self._client_id = client_id
        self._client_secret = client_secret
        self._redirect_uri = redirect_uri

    def authorize_url(self, state: str) -> str:
        query = urlencode(
            {
                "client_id": self._client_id,
                "redirect_uri": self._redirect_uri,
                "response_type": "code",
                "scope": SCOPES,
                "state": state,
            }
        )
        return f"{AUTHORIZE_URL}?{query}"

    def exchange_code(self, code: str) -> DiscordTokens:
        try:
            response = self._http.post(
                TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self._redirect_uri,
                },
                auth=(self._client_id, self._client_secret),
            )
        except httpx.HTTPError as exc:
            raise UpstreamError("Discord is unreachable") from exc
        if response.status_code in (400, 401):
            raise AuthenticationError("Discord rejected the authorization code")
        if response.is_error:
            raise UpstreamError(f"Discord returned HTTP {response.status_code}")
        try:
            return DiscordTokens.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise UpstreamError("Discord returned an unexpected token response") from exc

    def get_current_user(self, access_token: str) -> DiscordUser:
        try:
            response = self._http.get(
                CURRENT_USER_URL, headers={"Authorization": f"Bearer {access_token}"}
            )
        except httpx.HTTPError as exc:
            raise UpstreamError("Discord is unreachable") from exc
        if response.is_error:
            raise UpstreamError(f"Discord returned HTTP {response.status_code}")
        try:
            return DiscordUser.model_validate(response.json())
        except (ValueError, ValidationError) as exc:
            raise UpstreamError("Discord returned an unexpected user response") from exc
