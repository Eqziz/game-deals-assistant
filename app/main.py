from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests

from .db import (
    init_db,
    get_or_create_demo_user,
    add_favorite,
    list_favorites,
    delete_favorite,
    upsert_connected_account,
    list_connected_accounts,
    upsert_owned_game,
    bulk_upsert_owned_games,
    list_owned_games,
    delete_owned_game,
    owned_game_keys,
)

from .sources.steam import fetch_steam_specials, fetch_owned_steam_games
from .sources.cheapshark import fetch_deals as fetch_cheapshark_deals, fetch_stores


app = FastAPI(title="Game Deals Assistant")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


class FavoriteCreate(BaseModel):
    title: str
    store_name: str
    deal_url: str
    sale_price: float
    normal_price: float
    savings: float
    target_price: float | None = None


class ManualOwnedGameCreate(BaseModel):
    platform: str
    platform_game_id: str | None = None
    title: str
    playtime_minutes: int = 0


class SteamSyncRequest(BaseModel):
    steam_id: str


@app.on_event("startup")
def startup():
    init_db()
    get_or_create_demo_user()


@app.get("/")
def index():
    return FileResponse("app/static/index.html")


@app.get("/api/me")
def me():
    return get_or_create_demo_user()


@app.get("/api/stores")
def stores():
    base_sources = [
        {"store_id": "steam_direct", "store_name": "Steam Direct"},
        {"store_id": "cheapshark_all", "store_name": "All PC Stores"},
    ]

    try:
        cheapshark_stores = fetch_stores()
    except requests.RequestException:
        cheapshark_stores = []

    return {
        "featured": base_sources,
        "all": base_sources + cheapshark_stores,
    }


def mark_owned(deals, user_id, hide_owned=False):
    keys = owned_game_keys(user_id)

    owned_titles = {
        game["title"].strip().lower()
        for game in list_owned_games(user_id)
        if game.get("title")
    }

    marked = []

    for deal in deals:
        store_name = (deal.get("store_name") or "").lower()
        source = deal.get("source") or ""
        platform_game_id = str(
            deal.get("platform_game_id")
            or deal.get("steam_app_id")
            or ""
        ).lower()

        title = (deal.get("title") or "").strip().lower()

        platform = "steam" if "steam" in store_name or source == "steam" else "unknown"

        is_owned = False

        if platform_game_id and (platform, platform_game_id) in keys:
            is_owned = True

        if title and title in owned_titles:
            is_owned = True

        deal["owned"] = is_owned

        if hide_owned and is_owned:
            continue

        marked.append(deal)

    return marked


@app.get("/api/deals")
def deals(
    min_discount: int = 10,
    max_discount: int = 100,
    store_id: str | None = None,
    title: str | None = None,
    max_price: float | None = Query(default=None),
    free_only: bool = False,
    source: str | None = None,
    hide_owned: bool = False,
    page: int = 0,
    page_size: int = 60,
):
    if min_discount < 0 or max_discount > 100 or min_discount > max_discount:
        raise HTTPException(status_code=400, detail="Invalid discount range.")

    if page < 0:
        raise HTTPException(status_code=400, detail="Invalid page number.")

    if page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Invalid page size.")

    user = get_or_create_demo_user()

    try:
        if source == "steam" or store_id == "steam_direct":
            all_steam_deals = fetch_steam_specials(
                min_discount=min_discount,
                max_discount=max_discount,
                title=title,
                max_price=max_price,
                free_only=free_only,
                cc="us",
                language="english",
            )

            marked_deals = mark_owned(
                all_steam_deals,
                user["id"],
                hide_owned=hide_owned,
            )

            start = page * page_size
            end = start + page_size

            page_deals = marked_deals[start:end]
            next_page = page + 1 if end < len(marked_deals) else None

            return {
                "deals": page_deals,
                "next_page": next_page,
            }

        real_store_id = None if store_id in (None, "", "cheapshark_all") else store_id

        loaded_result = fetch_cheapshark_deals(
            min_discount=min_discount,
            max_discount=max_discount,
            store_id=real_store_id,
            title=title,
            max_price=max_price,
            free_only=free_only,
            page_number=page,
            page_size=page_size,
        )

        marked_deals = mark_owned(
            loaded_result["deals"],
            user["id"],
            hide_owned=hide_owned,
        )

        return {
            "deals": marked_deals,
            "next_page": loaded_result["next_page"],
        }

    except requests.RequestException as error:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot load deals from external API: {error}"
        )


@app.post("/api/favorites")
def favorite_create(payload: FavoriteCreate):
    user = get_or_create_demo_user()

    add_favorite(
        user_id=user["id"],
        title=payload.title,
        store_name=payload.store_name,
        deal_url=payload.deal_url,
        sale_price=payload.sale_price,
        normal_price=payload.normal_price,
        savings=payload.savings,
        target_price=payload.target_price,
    )

    return {"status": "saved"}


@app.get("/api/favorites")
def favorite_list():
    user = get_or_create_demo_user()
    return list_favorites(user["id"])


@app.delete("/api/favorites/{favorite_id}")
def favorite_delete(favorite_id: int):
    user = get_or_create_demo_user()
    delete_favorite(favorite_id, user["id"])
    return {"status": "deleted"}


@app.get("/api/accounts")
def accounts():
    user = get_or_create_demo_user()
    return list_connected_accounts(user["id"])


@app.get("/api/owned-games")
def owned_games():
    user = get_or_create_demo_user()
    return list_owned_games(user["id"])


@app.post("/api/owned-games/manual")
def add_owned_game_manual(payload: ManualOwnedGameCreate):
    user = get_or_create_demo_user()

    platform = payload.platform.strip().lower()
    title = payload.title.strip()

    if not platform or not title:
        raise HTTPException(status_code=400, detail="Platform and title are required.")

    platform_game_id = payload.platform_game_id.strip() if payload.platform_game_id else title.lower()

    upsert_owned_game(
        user_id=user["id"],
        platform=platform,
        platform_game_id=platform_game_id,
        title=title,
        playtime_minutes=payload.playtime_minutes,
    )

    return {"status": "saved"}


@app.delete("/api/owned-games/{owned_game_id}")
def remove_owned_game(owned_game_id: int):
    user = get_or_create_demo_user()
    delete_owned_game(user["id"], owned_game_id)
    return {"status": "deleted"}


@app.post("/api/steam/sync")
def sync_steam_library(payload: SteamSyncRequest):
    user = get_or_create_demo_user()

    steam_id = payload.steam_id.strip()

    if not steam_id:
        raise HTTPException(status_code=400, detail="SteamID64 is required.")

    try:
        games = fetch_owned_steam_games(steam_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except requests.RequestException as error:
        raise HTTPException(status_code=503, detail=f"Steam API error: {error}")

    upsert_connected_account(user["id"], "steam", steam_id)
    bulk_upsert_owned_games(user["id"], games)

    return {
        "status": "synced",
        "steam_id": steam_id,
        "games_count": len(games),
    }