"""Unified in-house multi-store deals aggregator replacing CheapShark."""

from concurrent.futures import ThreadPoolExecutor
import logging
from typing import Dict, List, Optional
import requests

from .epic import fetch_epic_deals
from .gog import fetch_gog_deals
from .steam import fetch_steam_deals

logger = logging.getLogger(__name__)

STORE_PROVIDERS = [
    {"store_id": "steam", "store_name": "Steam", "icon_url": None},
    {"store_id": "gog", "store_name": "GOG", "icon_url": None},
    {"store_id": "epic", "store_name": "Epic Games Store", "icon_url": None},
]


def fetch_stores() -> List[Dict]:
    """Return all storefronts supported by our internal catalog API."""
    return list(STORE_PROVIDERS)


def fetch_catalog_deals(
    min_discount: int = 10,
    max_discount: int = 100,
    store_id: Optional[str] = None,
    title: Optional[str] = None,
    max_price: Optional[float] = None,
    free_only: bool = False,
    page: int = 0,
    page_size: int = 60,
) -> Dict:
    """Aggregate deals directly from Steam, GOG, and Epic Games Store."""
    selected = (store_id or "").strip().lower()

    if selected == "steam":
        res = fetch_steam_deals(
            min_discount=min_discount,
            max_discount=max_discount,
            title=title,
            max_price=max_price,
            free_only=free_only,
            page=page,
            page_size=page_size,
        )
        return {"deals": res["deals"], "next_page": res["next_page"], "unavailable_stores": []}

    if selected == "gog":
        res = fetch_gog_deals(
            min_discount=min_discount,
            max_discount=max_discount,
            title=title,
            max_price=max_price,
            free_only=free_only,
            page=page,
            page_size=min(page_size, 48),
        )
        return {"deals": res["deals"], "next_page": res["next_page"], "unavailable_stores": []}

    if selected == "epic":
        res = fetch_epic_deals(
            min_discount=min_discount,
            max_discount=max_discount,
            title=title,
            max_price=max_price,
            free_only=free_only,
            page=page,
            page_size=min(page_size, 40),
        )
        return {"deals": res["deals"], "next_page": res["next_page"], "unavailable_stores": []}

    # Aggregate across all supported storefronts in parallel.
    per_store = max(10, page_size // 3)
    tasks = {
        "steam": lambda: fetch_steam_deals(
            min_discount=min_discount, max_discount=max_discount,
            title=title, max_price=max_price, free_only=free_only,
            page=page, page_size=per_store,
        ),
        "gog": lambda: fetch_gog_deals(
            min_discount=min_discount, max_discount=max_discount,
            title=title, max_price=max_price, free_only=free_only,
            page=page, page_size=per_store,
        ),
        "epic": lambda: fetch_epic_deals(
            min_discount=min_discount, max_discount=max_discount,
            title=title, max_price=max_price, free_only=free_only,
            page=page, page_size=per_store,
        ),
    }

    combined_deals: List[Dict] = []
    unavailable_stores: List[str] = []
    has_next = False

    with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
        futures = {name: pool.submit(fn) for name, fn in tasks.items()}
        for name, future in futures.items():
            try:
                res = future.result()
                combined_deals.extend(res.get("deals") or [])
                if res.get("next_page") is not None:
                    has_next = True
            except requests.RequestException as error:
                logger.warning("Store %s failed (%s)", name, type(error).__name__)
                unavailable_stores.append(name)

    if len(unavailable_stores) == len(tasks):
        raise requests.RequestException("All catalog providers are temporarily unavailable")

    combined_deals.sort(key=lambda d: (-float(d.get("savings") or 0), float(d.get("sale_price") or 0)))

    return {
        "deals": combined_deals[:page_size],
        "next_page": page + 1 if has_next else None,
        "unavailable_stores": unavailable_stores,
    }
