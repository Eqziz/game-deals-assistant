from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import requests
import logging
from typing import Optional, List
from .db import *
from .sources.steam import fetch_steam_specials, fetch_owned_steam_games
from .sources.cheapshark import fetch_deals as fetch_cheapshark_deals, fetch_stores

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and demo user on startup (lifespan replaces deprecated on_event)."""
    try:
        init_db()
        get_or_create_demo_user()
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    yield

app = FastAPI(
    title="Game Deals Assistant",
    description="Personal Game Deals Assistant - Track game discounts, favorites, and your library",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

class FavoriteCreate(BaseModel):
    """Model for creating a favorite deal"""
    title: str = Field(..., min_length=1, max_length=500)
    store_name: str = Field(..., min_length=1, max_length=200)
    deal_url: str = Field(..., min_length=1, max_length=2000)
    sale_price: float = Field(..., ge=0)
    normal_price: float = Field(..., ge=0)
    savings: float = Field(..., ge=0, le=100)
    target_price: Optional[float] = Field(default=None, ge=0)

    @validator('sale_price', 'normal_price', 'target_price')
    def round_prices(cls, v):
        if v is not None:
            return round(v, 2)
        return v


class ManualOwnedGameCreate(BaseModel):
    """Model for manually adding an owned game"""
    platform: str = Field(..., min_length=1, max_length=50)
    platform_game_id: Optional[str] = Field(default=None, max_length=200)
    title: str = Field(..., min_length=1, max_length=500)
    playtime_minutes: int = Field(default=0, ge=0)


class SteamSyncRequest(BaseModel):
    """Model for Steam library sync request"""
    steam_id: str = Field(..., min_length=1, max_length=50)

@app.get("/")
def index():
    """Serve the main HTML page"""
    return FileResponse("app/static/index.html")


@app.get("/api/me")
def me():
    """Get current user information"""
    return get_or_create_demo_user()


@app.get("/api/stores")
def stores() -> dict:
    """Get available game stores"""
    featured = [
        {"store_id": "steam_direct", "store_name": "Steam Direct"},
        {"store_id": "cheapshark_all", "store_name": "All PC Stores"}
    ]
    try:
        cs = fetch_stores()
        logger.info(f"Successfully fetched {len(cs)} stores from CheapShark")
    except requests.RequestException as e:
        logger.warning(f"Failed to fetch CheapShark stores: {e}")
        cs = []
    return {"featured": featured, "all": featured + cs}

def mark_owned(deals: List[dict], user_id: int, hide_owned: bool = False) -> List[dict]:
    """Mark deals as owned and optionally hide them."""
    # Bug fix: was calling list_owned_games twice (once inside owned_game_keys, once directly).
    # Now we fetch once and build both keys and titles from the same result.
    all_owned = list_owned_games(user_id)
    keys: Set[Tuple[str, str]] = {
        (g["platform"], str(g["platform_game_id"]).lower())
        for g in all_owned if g.get("platform_game_id")
    }
    titles = {(g.get("title") or "").strip().lower() for g in all_owned if g.get("title")}
    out = []

    for d in deals:
        store = (d.get("store_name") or "").lower()
        platform = "steam" if "steam" in store or d.get("source") == "steam" else "unknown"
        gid = str(d.get("platform_game_id") or d.get("steam_app_id") or "").lower()
        title = (d.get("title") or "").strip().lower()

        owned = (gid and (platform, gid) in keys) or (title and title in titles)
        d["owned"] = bool(owned)

        if hide_owned and owned:
            continue
        out.append(d)

    return out


@app.get("/api/deals")
def deals(
    min_discount: int = Query(10, ge=0, le=100),
    max_discount: int = Query(100, ge=0, le=100),
    store_id: Optional[str] = None,
    title: Optional[str] = None,
    max_price: Optional[float] = Query(default=None, ge=0),
    free_only: bool = False,
    source: Optional[str] = None,
    hide_owned: bool = False
):
    """Get filtered game deals"""
    # Validate discount range
    if min_discount > max_discount:
        raise HTTPException(
            status_code=400,
            detail="min_discount cannot be greater than max_discount"
        )
    
    user = get_or_create_demo_user()
    
    try:
        if source == "steam" or store_id == "steam_direct":
            loaded = fetch_steam_specials(
                min_discount, max_discount, title, max_price, free_only,
                cc="us", language="english"
            )
            logger.info(f"Fetched {len(loaded)} Steam deals")
        else:
            real = None if store_id in (None, "", "cheapshark_all") else store_id
            loaded = fetch_cheapshark_deals(
                min_discount, max_discount, real, title, max_price, free_only
            )
            logger.info(f"Fetched {len(loaded)} CheapShark deals")
        
        return mark_owned(loaded, user["id"], hide_owned)
    
    except requests.RequestException as e:
        logger.error(f"Error fetching deals: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot load deals from external API: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in deals endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/favorites")
def favorite_create(p: FavoriteCreate):
    """Add a deal to favorites"""
    u = get_or_create_demo_user()
    try:
        add_favorite(
            u["id"], p.title, p.store_name, p.deal_url,
            p.sale_price, p.normal_price, p.savings, p.target_price
        )
        logger.info(f"Favorite added: {p.title}")
        return {"status": "saved"}
    except Exception as e:
        logger.error(f"Error saving favorite: {e}")
        raise HTTPException(status_code=500, detail="Error saving favorite")


@app.get("/api/favorites")
def favorite_list():
    """Get all favorite deals"""
    u = get_or_create_demo_user()
    return list_favorites(u["id"])


@app.delete("/api/favorites/{favorite_id}")
def favorite_delete(favorite_id: int):
    """Delete a favorite deal"""
    u = get_or_create_demo_user()
    try:
        deleted = delete_favorite(favorite_id, u["id"])
        if not deleted:
            raise HTTPException(status_code=404, detail="Favorite not found.")
        logger.info(f"Favorite deleted: {favorite_id}")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting favorite: {e}")
        raise HTTPException(status_code=500, detail="Error deleting favorite")


@app.get("/api/accounts")
def accounts():
    """Get connected accounts"""
    u = get_or_create_demo_user()
    return list_connected_accounts(u["id"])


@app.get("/api/owned-games")
def owned_games():
    """Get owned games"""
    u = get_or_create_demo_user()
    return list_owned_games(u["id"])


@app.post("/api/owned-games/manual")
def add_owned_game_manual(p: ManualOwnedGameCreate):
    """Manually add an owned game"""
    u = get_or_create_demo_user()
    platform = p.platform.strip().lower()
    title = p.title.strip()
    
    if not platform or not title:
        raise HTTPException(status_code=400, detail="Platform and title are required.")
    
    gid = p.platform_game_id.strip() if p.platform_game_id else title.lower()
    
    try:
        upsert_owned_game(u["id"], platform, gid, title, p.playtime_minutes)
        logger.info(f"Owned game added: {title} on {platform}")
        return {"status": "saved"}
    except Exception as e:
        logger.error(f"Error adding owned game: {e}")
        raise HTTPException(status_code=500, detail="Error adding owned game")


@app.delete("/api/owned-games/{owned_game_id}")
def remove_owned_game(owned_game_id: int):
    """Remove an owned game"""
    u = get_or_create_demo_user()
    try:
        deleted = delete_owned_game(u["id"], owned_game_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Owned game not found.")
        logger.info(f"Owned game deleted: {owned_game_id}")
        return {"status": "deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting owned game: {e}")
        raise HTTPException(status_code=500, detail="Error deleting owned game")


@app.post("/api/steam/sync")
def sync_steam_library(p: SteamSyncRequest):
    """Sync Steam library for the user"""
    u = get_or_create_demo_user()
    sid = p.steam_id.strip()
    
    if not sid:
        raise HTTPException(status_code=400, detail="SteamID64 is required.")
    
    try:
        logger.info(f"Starting Steam sync for user {u['id']} with SteamID {sid}")
        games = fetch_owned_steam_games(sid)
        logger.info(f"Fetched {len(games)} games from Steam")
        
        upsert_connected_account(u["id"], "steam", sid)
        bulk_upsert_owned_games(u["id"], games)
        
        logger.info(f"Steam sync completed: {len(games)} games synced")
        return {"status": "synced", "steam_id": sid, "games_count": len(games)}
    
    except ValueError as e:
        logger.warning(f"Steam sync validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except requests.RequestException as e:
        logger.error(f"Steam API error: {e}")
        raise HTTPException(status_code=503, detail=f"Steam API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error during Steam sync: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during Steam sync")