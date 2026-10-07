from fastapi.testclient import TestClient
from app.main import app
from app.db import init_db

client = TestClient(app)


def setup_module():
    init_db()


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "Game Deals Assistant"


def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Game Deals Assistant" in response.text


def test_me():
    response = client.get("/api/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "demo@local"


def test_stores():
    response = client.get("/api/stores")
    assert response.status_code == 200
    data = response.json()
    assert "featured" in data
    assert "all" in data
    assert len(data["all"]) > 0


def test_deals_api():
    response = client.get("/api/deals?min_discount=10&max_discount=100&page=0&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "deals" in data
    assert isinstance(data["deals"], list)
    if data["deals"]:
        deal = data["deals"][0]
        assert "title" in deal
        assert "sale_price" in deal
        assert "savings" in deal
        assert "deal_url" in deal
        assert "owned" in deal
        assert "is_favorite" in deal


def test_deals_validation_error():
    response = client.get("/api/deals?min_discount=90&max_discount=50")
    assert response.status_code == 400


def test_steam_direct_deals_pagination():
    response = client.get("/api/deals?source=steam&page=0&page_size=60")
    assert response.status_code == 200
    data = response.json()
    assert "deals" in data
    assert len(data["deals"]) > 10
    assert data["next_page"] == 1



def test_favorites_lifecycle():
    # 1. Add favorite
    payload = {
        "title": "Test Game Cyberpunk",
        "store_name": "Steam",
        "deal_url": "https://store.steampowered.com/app/999999",
        "sale_price": 19.99,
        "normal_price": 59.99,
        "savings": 66.67,
        "target_price": 14.99,
    }
    create_res = client.post("/api/favorites", json=payload)
    assert create_res.status_code == 200
    assert create_res.json()["status"] == "saved"

    # 2. List favorites
    list_res = client.get("/api/favorites")
    assert list_res.status_code == 200
    favorites = list_res.json()
    fav = next((f for f in favorites if f["deal_url"] == payload["deal_url"]), None)
    assert fav is not None
    assert fav["title"] == payload["title"]
    assert fav["target_price"] == payload["target_price"]

    # 3. Delete favorite by URL
    del_url_res = client.post("/api/favorites/delete-by-url", json={"deal_url": payload["deal_url"]})
    assert del_url_res.status_code == 200
    assert del_url_res.json()["status"] == "deleted"

    # Verify deleted
    list_after = client.get("/api/favorites").json()
    assert not any(f["deal_url"] == payload["deal_url"] for f in list_after)


def test_owned_games_lifecycle():
    # 1. Add manual owned game
    payload = {
        "platform": "epic",
        "title": "Hades II Test",
        "platform_game_id": "hades-2-test",
        "playtime_minutes": 120,
    }
    add_res = client.post("/api/owned-games/manual", json=payload)
    assert add_res.status_code == 200
    assert add_res.json()["status"] == "saved"

    # 2. List owned games
    list_res = client.get("/api/owned-games")
    assert list_res.status_code == 200
    games = list_res.json()
    owned = next((g for g in games if g["title"] == payload["title"]), None)
    assert owned is not None
    assert owned["platform"] == "epic"

    # 3. Delete owned game
    del_res = client.delete(f"/api/owned-games/{owned['id']}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "deleted"

