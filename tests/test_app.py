import os
from uuid import uuid4

import psycopg
import pytest
import requests
from fastapi.testclient import TestClient
from psycopg import sql

from app import db, main


@pytest.fixture(scope="session", autouse=True)
def isolated_database():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.fail("Set TEST_DATABASE_URL to a disposable PostgreSQL database")
    schema = "qa_" + uuid4().hex
    with psycopg.connect(url, autocommit=True) as admin, pytest.MonkeyPatch.context() as env:
        admin.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
        try:
            env.setenv("DATABASE_URL", url)
            env.setenv("PGOPTIONS", "-c search_path=" + schema)
            env.setenv("PUBLIC_BASE_URL", "https://testserver")
            env.setenv("SESSION_SECRET", "test-only-session-secret-" + "x" * 24)
            db.init_db()
            yield
        finally:
            admin.execute(sql.SQL("DROP SCHEMA {} CASCADE").format(sql.Identifier(schema)))


@pytest.fixture
def client():
    with TestClient(main.app, base_url="https://testserver", headers={"Origin": "https://testserver"}) as browser:
        yield browser


def sign_in(client, subject):
    user = db.get_or_create_google_user(subject, subject + "@example.org", subject)
    client.cookies.set("gda_session", db.create_session(user["id"]))
    return user


DEAL = {
    "title": "Hades", "store_name": "Steam", "deal_url": "https://store.steampowered.com/app/1145360/",
    "sale_price": 4.99, "normal_price": 24.99, "savings": 80, "target_price": 4.99,
}


def test_public_endpoints(client, monkeypatch):
    monkeypatch.setattr(main, "fetch_stores", lambda: [{"store_id": "1", "store_name": "Steam"}])
    monkeypatch.setattr(main, "fetch_cheapshark_deals", lambda **kw: {"deals": [DEAL.copy()], "next_page": 1})
    assert client.get("/").status_code == 200
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/api/me").json() == {"authenticated": False, "user": None}
    assert client.get("/api/stores").json()["all"][-1]["store_name"] == "Steam"
    result = client.get("/api/deals").json()
    assert result["next_page"] == 1
    assert result["deals"][0]["owned"] is False
    assert result["deals"][0]["is_favorite"] is False
    assert client.get("/api/deals?min_discount=80&max_discount=10").status_code == 400


@pytest.mark.parametrize("method,url,body", [
    ("GET", "/api/favorites", None), ("GET", "/api/owned-games", None),
    ("GET", "/api/accounts", None), ("POST", "/api/favorites", DEAL),
    ("PUT", "/api/accounts", {"platform": "xbox", "platform_user_id": "gamertag"}),
    ("DELETE", "/api/accounts/1", None),
    ("POST", "/api/owned-games/manual", {"platform": "steam", "title": "Hades"}),
    ("POST", "/api/steam/sync", {"steam_id": "76561198000000000"}),
])
def test_personal_actions_require_login(client, method, url, body):
    assert client.request(method, url, json=body).status_code == 401


def test_account_isolation_and_second_device(client):
    owner = "owner-" + uuid4().hex
    sign_in(client, owner)
    assert client.get("/api/me").json()["user"]["email"] == owner + "@example.org"
    assert client.post("/api/favorites", json=DEAL).is_success
    favorite = client.get("/api/favorites").json()[0]
    assert favorite["target_price"] == 4.99
    assert client.post("/api/owned-games/manual", json={"platform": "steam", "title": "Hades"}).is_success
    game = client.get("/api/owned-games").json()[0]

    sign_in(client, uuid4().hex)
    assert client.get("/api/favorites").json() == []
    assert client.get("/api/owned-games").json() == []
    assert client.delete(f"/api/favorites/{favorite['id']}").status_code == 404
    assert client.delete(f"/api/owned-games/{game['id']}").status_code == 404
    assert client.post("/api/favorites", json={**DEAL, "target_price": 1}).is_success
    assert client.post("/api/favorites/delete-by-url", json={"deal_url": DEAL["deal_url"]}).is_success

    sign_in(client, owner)
    assert client.get("/api/favorites").json()[0]["target_price"] == 4.99
    assert client.get("/api/owned-games").json()[0]["id"] == game["id"]
    assert client.delete(f"/api/favorites/{favorite['id']}").is_success
    assert client.delete(f"/api/owned-games/{game['id']}").is_success


def test_game_profiles_are_private_and_updatable(client, monkeypatch):
    owner = uuid4().hex
    sign_in(client, owner)
    profile = {"platform": "Example Network", "platform_user_id": "Player One"}
    assert client.put("/api/accounts", json=profile).is_success
    profile["platform_user_id"] = "https://example.org/players/two"
    assert client.put("/api/accounts", json=profile).is_success
    entry, = client.get("/api/accounts").json()
    assert entry["platform_user_id"] == profile["platform_user_id"]
    sign_in(client, uuid4().hex)
    assert client.get("/api/accounts").json() == []
    assert client.delete(f"/api/accounts/{entry['id']}").status_code == 404
    sign_in(client, owner)
    assert client.delete(f"/api/accounts/{entry['id']}").is_success
    assert client.get("/api/accounts").json() == []

    monkeypatch.setattr(main, "fetch_owned_steam_games", lambda _: [
        {"platform_game_id": "1145360", "title": "Hades", "playtime_minutes": 30}
    ])
    assert client.post("/api/steam/sync", json={"steam_id": "76561198000000000"}).is_success
    steam, = client.get("/api/accounts").json()
    assert steam["platform"] == "steam"
    assert client.delete(f"/api/accounts/{steam['id']}").is_success
    assert client.get("/api/owned-games").json()[0]["title"] == "Hades"


def test_cross_origin_and_revocation(client):
    sign_in(client, uuid4().hex)
    token = client.cookies.get("gda_session")
    assert client.post("/api/favorites", json=DEAL, headers={"Origin": "https://elsewhere.example"}).status_code == 403
    assert client.post("/auth/logout").is_success
    client.cookies.clear()
    client.cookies.set("gda_session", token)
    assert client.get("/api/favorites").status_code == 401


def test_upstream_failures_are_retryable_and_private(client, monkeypatch, caplog):
    sign_in(client, uuid4().hex)
    def unavailable(*args, **kwargs):
        raise requests.ConnectionError("private-upstream-marker")
    monkeypatch.setattr(main, "fetch_owned_steam_games", unavailable)
    response = client.post("/api/steam/sync", json={"steam_id": "76561198000000000"})
    assert response.status_code == 503
    monkeypatch.setattr(main, "fetch_steam_deals", unavailable)
    catalog = client.get("/api/deals?source=steam")
    assert catalog.status_code == 503
    assert "private-upstream-marker" not in response.text + catalog.text + caplog.text
    monkeypatch.setattr(main, "fetch_steam_deals", lambda **kw: {"deals": [], "next_page": None})
    assert client.get("/api/deals?source=steam").json() == {"deals": [], "next_page": None}

def test_google_login_round_trip(client, monkeypatch):
    from app import auth
    from fastapi.responses import RedirectResponse

    monkeypatch.setattr(auth, "_configured", lambda: True)
    monkeypatch.setattr(auth, "PUBLIC_BASE_URL", "https://testserver")
    subject = uuid4().hex

    async def provider_redirect(request, callback_url):
        assert callback_url == "https://testserver/auth/callback"
        return RedirectResponse("https://accounts.google.com/")

    async def verified_response(request):
        return {"userinfo": {"sub": subject, "email": "player@example.org", "email_verified": True, "name": "Player"}}

    monkeypatch.setattr(auth.google, "authorize_redirect", provider_redirect)
    monkeypatch.setattr(auth.google, "authorize_access_token", verified_response)
    start = client.get("/auth/login", params={"next": "/#favorites"}, follow_redirects=False)
    assert start.headers["location"] == "https://accounts.google.com/"
    completed = client.get("/auth/callback", follow_redirects=False)
    assert completed.headers["location"] == "/#favorites"
    cookie = next(c for c in completed.headers.get_list("set-cookie") if c.startswith("gda_session="))
    assert all(flag in cookie.lower() for flag in ("httponly", "secure", "samesite=lax"))
    assert client.get("/api/me").json()["user"]["name"] == "Player"

    async def rejected_response(request):
        raise ValueError("invalid provider response")

    monkeypatch.setattr(auth.google, "authorize_access_token", rejected_response)
    client.get("/auth/login", follow_redirects=False)
    rejected = client.get("/auth/callback", follow_redirects=False)
    assert rejected.headers["location"] == "/?auth_error=failed"
    assert all(not c.startswith("gda_session=") for c in rejected.headers.get_list("set-cookie"))


def test_migration_is_repeatable_and_subject_is_stable():
    subject = uuid4().hex
    user = db.get_or_create_google_user(subject, "first@example.org", "Original")
    db.init_db()
    updated = db.get_or_create_google_user(subject, "new@example.org", "New")
    assert updated["id"] == user["id"]
    assert updated["email"] == "new@example.org"
