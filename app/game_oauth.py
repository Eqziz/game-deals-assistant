"""OAuth 2.0 direct profile connection for non-Steam gaming platforms."""

import os
from urllib.parse import urlencode

import httpx

_PROVIDERS = {
    "epic": {
        "client_id_env": "EPIC_CLIENT_ID",
        "client_secret_env": "EPIC_CLIENT_SECRET",
        "authorize_url": "https://www.epicgames.com/id/authorize",
        "token_url": "https://api.epicgames.dev/epic/oauth/v2/token",
        "userinfo_url": "https://api.epicgames.dev/epic/oauth/v2/userInfo",
        "scope": "basic_profile",
        "id_field": "sub",
        "name_field": "preferred_username",
    },
    "gog": {
        "client_id_env": "GOG_CLIENT_ID",
        "client_secret_env": "GOG_CLIENT_SECRET",
        "authorize_url": "https://auth.gog.com/auth",
        "token_url": "https://auth.gog.com/token",
        "userinfo_url": "https://embed.gog.com/userData.json",
        "scope": "",
        "id_field": "userId",
        "name_field": "username",
    },
    "xbox": {
        "client_id_env": "XBOX_CLIENT_ID",
        "client_secret_env": "XBOX_CLIENT_SECRET",
        "authorize_url": "https://login.live.com/oauth20_authorize.srf",
        "token_url": "https://login.live.com/oauth20_token.srf",
        "userinfo_url": "https://apis.live.net/v5.0/me",
        "scope": "XboxLive.signin",
        "id_field": "id",
        "name_field": "name",
    },
    "battlenet": {
        "client_id_env": "BATTLENET_CLIENT_ID",
        "client_secret_env": "BATTLENET_CLIENT_SECRET",
        "authorize_url": "https://oauth.battle.net/authorize",
        "token_url": "https://oauth.battle.net/token",
        "userinfo_url": "https://oauth.battle.net/userinfo",
        "scope": "openid",
        "id_field": "sub",
        "name_field": "battletag",
    },
}


def _credentials(platform: str) -> tuple[str, str]:
    cfg = _PROVIDERS[platform]
    return (
        os.environ.get(cfg["client_id_env"], "").strip(),
        os.environ.get(cfg["client_secret_env"], "").strip(),
    )


def providers() -> dict[str, bool]:
    """Return availability map for all configured OAuth gaming platforms."""
    return {
        platform: bool(all(_credentials(platform)))
        for platform in _PROVIDERS
    }


async def start(request, platform: str, state: str, redirect_uri: str) -> str:
    """Build the provider OAuth2 authorization URL."""
    if platform not in _PROVIDERS:
        raise ValueError(f"Unsupported platform: {platform}")
    client_id, client_secret = _credentials(platform)
    if not (client_id and client_secret):
        raise RuntimeError(f"OAuth not configured for {platform}")

    cfg = _PROVIDERS[platform]
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "state": state,
    }
    if cfg["scope"]:
        params["scope"] = cfg["scope"]
    return cfg["authorize_url"] + "?" + urlencode(params)


async def verify(request, platform: str) -> tuple[str, str]:
    """Exchange authorization code for access token and fetch verified identity."""
    if platform not in _PROVIDERS:
        raise ValueError(f"Unsupported platform: {platform}")
    code = request.query_params.get("code", "").strip()
    if not code:
        raise ValueError("Missing OAuth authorization code")

    client_id, client_secret = _credentials(platform)
    if not (client_id and client_secret):
        raise RuntimeError(f"OAuth not configured for {platform}")

    cfg = _PROVIDERS[platform]
    redirect_uri = str(request.url).split("?", 1)[0]

    async with httpx.AsyncClient(timeout=15) as client:
        token_resp = await client.post(
            cfg["token_url"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Accept": "application/json"},
        )
        token_resp.raise_for_status()
        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise ValueError("Missing access token from provider")

        user_resp = await client.get(
            cfg["userinfo_url"],
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )
        user_resp.raise_for_status()
        profile = user_resp.json()

    subject = str(profile.get(cfg["id_field"]) or profile.get("account_id") or token_data.get("account_id") or "").strip()
    if not subject:
        raise ValueError("Provider did not return a user identifier")
    display_name = str(profile.get(cfg["name_field"]) or profile.get("displayName") or subject).strip()
    return subject, display_name
