import logging
import time
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.cheapshark.com/api/1.0"
HEADERS = {
    "User-Agent": "GameDealsAssistant/1.0 (https://github.com/nodir270/game-deals-assistant; contact@gamedeals.local)",
    "Accept": "application/json",
}

_stores_cache: List[Dict] = []
_stores_cache_time: float = 0.0
CACHE_TTL_SECONDS = 3600.0


def fetch_stores(force_refresh: bool = False) -> List[Dict]:
    """Fetch all active game stores from CheapShark API with in-memory caching."""
    global _stores_cache, _stores_cache_time
    now = time.time()

    if not force_refresh and _stores_cache and (now - _stores_cache_time < CACHE_TTL_SECONDS):
        return _stores_cache

    try:
        response = requests.get(f"{BASE_URL}/stores", headers=HEADERS, timeout=20)
        response.raise_for_status()
        raw_stores = response.json()

        active_stores = []
        for store in raw_stores:
            is_active = store.get("isActive")
            if is_active == 1 or is_active == "1":
                store_id = str(store.get("storeID"))
                images = store.get("images") or {}
                icon_path = images.get("icon")
                icon_url = f"https://www.cheapshark.com{icon_path}" if icon_path else None

                active_stores.append({
                    "store_id": store_id,
                    "store_name": store.get("storeName"),
                    "icon_url": icon_url,
                })

        _stores_cache = active_stores
        _stores_cache_time = now
        logger.info(f"Loaded and cached {len(active_stores)} CheapShark stores")
        return _stores_cache

    except requests.RequestException as error:
        logger.error(f"Error fetching CheapShark stores: {error}")
        if _stores_cache:
            return _stores_cache
        raise


def get_store_map() -> Dict[str, Dict]:
    """Return dictionary mapping store_id to store info."""
    try:
        stores = fetch_stores()
        return {s["store_id"]: s for s in stores}
    except Exception:
        return {}


def fetch_deals(
    min_discount: int = 10,
    max_discount: int = 100,
    store_id: Optional[str] = None,
    title: Optional[str] = None,
    max_price: Optional[float] = None,
    free_only: bool = False,
    page_size: int = 60,
    page_number: int = 0,
    max_scan_pages: int = 3,
) -> Dict:
    """
    Fetch deals from CheapShark API with server-side filtering and pagination.
    Note: CheapShark desc=0 sorts descending (highest savings first).
    """
    store_map = get_store_map()

    result = []
    current_page = page_number
    scanned_pages = 0
    next_page = None

    while scanned_pages < max_scan_pages:
        params: Dict[str, str | int | float] = {
            "pageSize": page_size,
            "pageNumber": current_page,
            "sortBy": "Savings",
            "desc": 0,  # 0 = descending in CheapShark
            "onSale": 1,
        }

        if free_only:
            params["upperPrice"] = 0
        elif max_price is not None:
            params["upperPrice"] = float(max_price)

        if store_id:
            params["storeID"] = str(store_id)

        if title:
            params["title"] = title.strip()

        try:
            response = requests.get(f"{BASE_URL}/deals", params=params, headers=HEADERS, timeout=20)
            response.raise_for_status()
            raw_deals = response.json()
        except requests.RequestException as error:
            logger.error(f"CheapShark deals request failed: {error}")
            raise

        if not raw_deals:
            next_page = None
            break

        for deal in raw_deals:
            try:
                savings = float(deal.get("savings", 0))
                sale_price = float(deal.get("salePrice", 0))
                normal_price = float(deal.get("normalPrice", 0))
            except (ValueError, TypeError):
                continue

            if not (float(min_discount) <= savings <= float(max_discount)):
                continue

            if max_price is not None and sale_price > float(max_price):
                continue

            if free_only and sale_price != 0:
                continue

            deal_store_id = str(deal.get("storeID"))
            store_info = store_map.get(deal_store_id, {})
            store_name = store_info.get("store_name", f"Store #{deal_store_id}")
            store_icon = store_info.get("icon_url")
            steam_app_id = deal.get("steamAppID")
            deal_id = deal.get("dealID")

            steam_rating_percent = deal.get("steamRatingPercent")
            steam_rating_text = deal.get("steamRatingText")
            metacritic_score = deal.get("metacriticScore")
            deal_rating = deal.get("dealRating")

            result.append({
                "deal_id": deal_id,
                "title": deal.get("title") or "Unknown game",
                "platform_game_id": str(steam_app_id) if steam_app_id else "",
                "store_id": deal_store_id,
                "store_name": store_name,
                "store_icon": store_icon,
                "sale_price": round(sale_price, 2),
                "normal_price": round(normal_price, 2),
                "savings": round(savings, 2),
                "thumb": deal.get("thumb") or "",
                "steam_app_id": str(steam_app_id) if steam_app_id else "",
                "deal_url": f"https://www.cheapshark.com/redirect?dealID={deal_id}",
                "source": "cheapshark",
                "steam_rating_percent": int(steam_rating_percent) if steam_rating_percent and steam_rating_percent != "0" else None,
                "steam_rating_text": steam_rating_text if steam_rating_text else None,
                "metacritic_score": int(metacritic_score) if metacritic_score and metacritic_score != "0" else None,
                "deal_rating": float(deal_rating) if deal_rating and deal_rating != "0" else None,
            })

        has_more_raw_pages = len(raw_deals) == page_size
        next_page = current_page + 1 if has_more_raw_pages else None

        if result or not has_more_raw_pages:
            break

        current_page += 1
        scanned_pages += 1

    return {
        "deals": result,
        "next_page": next_page,
    }