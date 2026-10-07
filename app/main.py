import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import requests

from .db import (
    init_db,
    get_or_create_demo_user,
    add_favorite,
    list_favorites,
    delete_favorite,
    delete_favorite_by_url,
    favorite_deal_urls,
    upsert_connected_account,
    list_connected_accounts,
    upsert_owned_game,
    bulk_upsert_owned_games,
    list_owned_games,
    delete_owned_game,
    owned_game_keys,
)
from .sources.cheapshark import fetch_deals as fetch_cheapshark_deals, fetch_stores
from .sources.steam import fetch_owned_steam_games, fetch_steam_deals, fetch_steam_specials

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and demo user on application startup."""
    init_db()
    get_or_create_demo_user()
    logger.info("Application started and database ready")
    yield


app = FastAPI(
    title="Game Deals Assistant",
    description="Track discounts across Steam, CheapShark, manage game library and favorites.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


class FavoriteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    store_name: str
    deal_url: str
    sale_price: float = Field(..., ge=0)
    normal_price: float = Field(..., ge=0)
    savings: float = Field(..., ge=0, le=100)
    target_price: Optional[float] = Field(default=None, ge=0)


class FavoriteDeleteRequest(BaseModel):
    deal_url: str


class ManualOwnedGameCreate(BaseModel):
    platform: str
    platform_game_id: Optional[str] = None
    title: str = Field(..., min_length=1)
    playtime_minutes: int = Field(default=0, ge=0)


class SteamSyncRequest(BaseModel):
    steam_id: str = Field(..., min_length=5)


@app.get("/")
def index():
    return FileResponse("app/static/index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": "Game Deals Assistant",
        "version": "1.0.0",
    }


@app.get("/api/me")
def me():
    return get_or_create_demo_user()


@app.get("/api/stores")
def stores():
    base_sources = [
        {"store_id": "steam_direct", "store_name": "Steam Direct", "icon_url": None},
        {"store_id": "cheapshark_all", "store_name": "All PC Stores", "icon_url": None},
    ]

    try:
        cheapshark_stores = fetch_stores()
    except requests.RequestException as error:
        logger.warning(f"Could not load CheapShark stores: {error}")
        cheapshark_stores = []

    return {
        "featured": base_sources,
        "all": base_sources + cheapshark_stores,
    }


def mark_deals(deals, user_id: int, hide_owned: bool = False):
    """Mark deals with ownership and favorite flags, and filter owned if requested."""
    keys = owned_game_keys(user_id)
    fav_urls = favorite_deal_urls(user_id)

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
        elif title and title in owned_titles:
            is_owned = True

        deal["owned"] = is_owned
        deal["is_favorite"] = deal.get("deal_url") in fav_urls

        if hide_owned and is_owned:
            continue

        marked.append(deal)

    return marked


@app.get("/api/deals")
def deals(
    min_discount: int = Query(default=10, ge=0, le=100),
    max_discount: int = Query(default=100, ge=0, le=100),
    store_id: Optional[str] = None,
    title: Optional[str] = None,
    max_price: Optional[float] = Query(default=None, ge=0),
    free_only: bool = False,
    source: Optional[str] = None,
    hide_owned: bool = False,
    page: int = Query(default=0, ge=0),
    page_size: int = Query(default=60, ge=1, le=100),
):
    if min_discount > max_discount:
        raise HTTPException(status_code=400, detail="min_discount cannot be greater than max_discount.")

    user = get_or_create_demo_user()

    try:
        if source == "steam" or store_id == "steam_direct":
            steam_result = fetch_steam_deals(
                min_discount=min_discount,
                max_discount=max_discount,
                title=title,
                max_price=max_price,
                free_only=free_only,
                page=page,
                page_size=page_size,
                cc="us",
                language="english",
            )

            marked = mark_deals(steam_result["deals"], user["id"], hide_owned=hide_owned)

            return {
                "deals": marked,
                "next_page": steam_result["next_page"],
            }

        real_store_id = None if store_id in (None, "", "cheapshark_all") else store_id

        loaded = fetch_cheapshark_deals(
            min_discount=min_discount,
            max_discount=max_discount,
            store_id=real_store_id,
            title=title,
            max_price=max_price,
            free_only=free_only,
            page_number=page,
            page_size=page_size,
        )

        marked = mark_deals(loaded["deals"], user["id"], hide_owned=hide_owned)

        return {
            "deals": marked,
            "next_page": loaded["next_page"],
        }

    except requests.RequestException as error:
        logger.error(f"External API error: {error}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot load deals from external API: {error}",
        )


@app.post("/api/favorites")
def favorite_create(payload: FavoriteCreate):
    user = get_or_create_demo_user()

    add_favorite(
        user_id=user["id"],
        title=payload.title.strip(),
        store_name=payload.store_name.strip(),
        deal_url=payload.deal_url.strip(),
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
    deleted = delete_favorite(favorite_id, user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"status": "deleted"}


@app.post("/api/favorites/delete-by-url")
def favorite_delete_by_url(payload: FavoriteDeleteRequest):
    user = get_or_create_demo_user()
    deleted = delete_favorite_by_url(payload.deal_url.strip(), user["id"])
    return {"status": "deleted" if deleted else "not_found"}


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
    deleted = delete_owned_game(user["id"], owned_game_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Owned game not found")
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