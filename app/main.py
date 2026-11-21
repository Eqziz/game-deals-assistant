import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator
import requests

from .auth import install_auth, optional_user, require_user
from .db import (
    init_db,
    check_db,
    add_favorite,
    list_favorites,
    delete_favorite,
    delete_favorite_by_url,
    favorite_deal_urls,
    save_steam_library,
    list_connected_accounts,
    upsert_owned_game,
    list_owned_games,
    delete_owned_game,
    owned_game_keys,
)
from .sources.cheapshark import fetch_deals as fetch_cheapshark_deals, fetch_stores
from .sources.steam import (
    PrivateSteamLibrary, SteamConfigurationError, fetch_owned_steam_games, fetch_steam_deals,
)

logger = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Application started and database ready")
    yield


app = FastAPI(
    title="Game Deals Assistant",
    description="Track discounts across Steam, CheapShark, manage game library and favorites.",
    version="1.0.0",
    lifespan=lifespan,
)

install_auth(app)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class InputModel(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, allow_inf_nan=False)


class DealLink(InputModel):
    deal_url: str = Field(min_length=1, max_length=4096)

    @field_validator("deal_url")
    @classmethod
    def check_link(cls, value):
        url = urlsplit(value)
        if (url.scheme not in {"http", "https"} or not url.hostname or url.username
                or url.password or "\\" in value or any(ord(ch) < 32 for ch in value)):
            raise ValueError("A valid HTTP or HTTPS store link is required.")
        return value


class FavoriteCreate(DealLink):
    title: str = Field(min_length=1, max_length=512)
    store_name: str = Field(min_length=1, max_length=128)
    sale_price: float = Field(..., ge=0, le=999_999_999_999.99)
    normal_price: float = Field(..., ge=0, le=999_999_999_999.99)
    savings: float = Field(..., ge=0, le=100)
    target_price: Optional[float] = Field(default=None, ge=0, le=999_999_999_999.99)


class ManualOwnedGameCreate(InputModel):
    platform: str = Field(min_length=1, max_length=64)
    platform_game_id: Optional[str] = Field(default=None, max_length=512)
    title: str = Field(min_length=1, max_length=512)
    playtime_minutes: int = Field(default=0, ge=0, le=2_147_483_647)


class SteamSyncRequest(InputModel):
    steam_id: str = Field(pattern=r"^[0-9]{17}$")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/ready")
@app.get("/api/health")
def health():
    try:
        check_db()
    except Exception as error:
        logger.error("Database readiness failed (%s)", type(error).__name__)
        raise HTTPException(503, "Database unavailable.") from None
    return {
        "status": "ok",
        "app": "Game Deals Assistant",
        "version": "1.0.0",
    }


@app.get("/api/me")
def me(user=Depends(optional_user)):
    profile = {"name": user["name"], "email": user["email"]} if user else None
    return {"authenticated": bool(user), "user": profile}


@app.get("/api/stores")
def stores():
    base_sources = [
        {"store_id": "steam_direct", "store_name": "Steam Direct", "icon_url": None},
        {"store_id": "cheapshark_all", "store_name": "All PC Stores", "icon_url": None},
    ]

    try:
        cheapshark_stores = fetch_stores()
    except requests.RequestException as error:
        logger.warning("Could not load CheapShark stores (%s)", type(error).__name__)
        cheapshark_stores = []

    return {
        "featured": base_sources,
        "all": base_sources + cheapshark_stores,
    }


def mark_deals(deals, user_id: Optional[int], hide_owned: bool = False):
    """Mark deals with ownership and favorite flags, and filter owned if requested."""
    if user_id is None:
        return [dict(deal, owned=False, is_favorite=False) for deal in deals]
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

        if hide_owned and is_owned:
            continue

        marked.append(dict(deal, owned=is_owned, is_favorite=deal.get("deal_url") in fav_urls))

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
    user=Depends(optional_user),
):
    if min_discount > max_discount:
        raise HTTPException(status_code=400, detail="min_discount cannot be greater than max_discount.")

    user_id = user["id"] if user else None

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

            marked = mark_deals(steam_result["deals"], user_id, hide_owned=hide_owned)

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

        marked = mark_deals(loaded["deals"], user_id, hide_owned=hide_owned)

        return {
            "deals": marked,
            "next_page": loaded["next_page"],
        }

    except requests.RequestException as error:
        logger.warning("Catalog provider failed (%s)", type(error).__name__)
        raise HTTPException(
            status_code=503,
            detail="Catalog provider temporarily unavailable.",
        ) from None


@app.post("/api/favorites")
def favorite_create(payload: FavoriteCreate, user=Depends(require_user)):
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
def favorite_list(user=Depends(require_user)):
    return list_favorites(user["id"])


@app.delete("/api/favorites/{favorite_id}")
def favorite_delete(favorite_id: int, user=Depends(require_user)):
    deleted = delete_favorite(favorite_id, user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return {"status": "deleted"}


@app.post("/api/favorites/delete-by-url")
def favorite_delete_by_url(payload: DealLink, user=Depends(require_user)):
    deleted = delete_favorite_by_url(payload.deal_url.strip(), user["id"])
    return {"status": "deleted" if deleted else "not_found"}


@app.get("/api/accounts")
def accounts(user=Depends(require_user)):
    return list_connected_accounts(user["id"])


@app.get("/api/owned-games")
def owned_games(user=Depends(require_user)):
    return list_owned_games(user["id"])


@app.post("/api/owned-games/manual")
def add_owned_game_manual(payload: ManualOwnedGameCreate, user=Depends(require_user)):
    title = payload.title
    platform_game_id = payload.platform_game_id or title.lower()

    upsert_owned_game(
        user_id=user["id"],
        platform=payload.platform.lower(),
        platform_game_id=platform_game_id,
        title=title,
        playtime_minutes=payload.playtime_minutes,
    )

    return {"status": "saved"}


@app.delete("/api/owned-games/{owned_game_id}")
def remove_owned_game(owned_game_id: int, user=Depends(require_user)):
    deleted = delete_owned_game(user["id"], owned_game_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Owned game not found")
    return {"status": "deleted"}


@app.post("/api/steam/sync")
def sync_steam_library(payload: SteamSyncRequest, user=Depends(require_user)):
    steam_id = payload.steam_id
    try:
        games = fetch_owned_steam_games(steam_id)
    except SteamConfigurationError:
        raise HTTPException(503, "Steam sync is unavailable.") from None
    except PrivateSteamLibrary:
        raise HTTPException(422, "Steam library unavailable. Check the SteamID and game visibility.") from None
    except requests.RequestException as error:
        logger.warning("Steam library request failed (%s)", type(error).__name__)
        raise HTTPException(503, "Steam is temporarily unavailable.") from None

    save_steam_library(user["id"], steam_id, games)

    return {
        "status": "synced",
        "steam_id": steam_id,
        "games_count": len(games),
    }
