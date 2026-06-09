import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

BASE_URL = "https://www.cheapshark.com/api/1.0"


def fetch_stores() -> List[Dict]:
    """Fetch all active stores from CheapShark"""
    try:
        r = requests.get(f"{BASE_URL}/stores", timeout=20)
        r.raise_for_status()
        stores = r.json()
        result = [
            {"store_id": str(s.get("storeID")), "store_name": s.get("storeName")}
            for s in stores
            if s.get("isActive") in (1, "1")
        ]
        logger.info(f"Fetched {len(result)} stores from CheapShark")
        return result
    except requests.RequestException as e:
        logger.error(f"Error fetching CheapShark stores: {e}")
        raise


def fetch_deals(
    min_discount: int = 10,
    max_discount: int = 100,
    store_id: Optional[str] = None,
    title: Optional[str] = None,
    max_price: Optional[float] = None,
    free_only: bool = False,
    page_size: int = 60,
    max_results: int = 1000
) -> List[Dict]:
    """
    Fetch game deals from CheapShark API
    
    Args:
        min_discount: Minimum discount percentage
        max_discount: Maximum discount percentage
        store_id: Specific store to filter by
        title: Game title to search for
        max_price: Maximum price filter
        free_only: Only return free games
        page_size: Results per page
        max_results: Maximum total results to fetch
    
    Returns:
        List of deals
    """
    all_deals = []
    page_number = 0

    # Try to fetch stores for name mapping
    try:
        stores = fetch_stores()
        store_map = {store["store_id"]: store["store_name"] for store in stores}
    except requests.RequestException:
        logger.warning("Could not fetch store names, using store IDs")
        store_map = {}

    while len(all_deals) < max_results:
        params = {
            "pageSize": page_size,
            "pageNumber": page_number,
            "sortBy": "Savings",
            "desc": "1",
            "lowerPrice": "0",
            "upperPrice": "1000",
        }

        if store_id:
            params["storeID"] = store_id

        if title:
            params["title"] = title

        try:
            response = requests.get(
                f"{BASE_URL}/deals",
                params=params,
                timeout=20
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Error fetching CheapShark deals: {e}")
            raise

        raw_deals = response.json()

        if not raw_deals:
            logger.info(f"No more deals found at page {page_number}")
            break

        for deal in raw_deals:
            savings = float(deal.get("savings", 0))
            sale_price = float(deal.get("salePrice", 0))
            normal_price = float(deal.get("normalPrice", 0))

            # Apply filters
            if not (float(min_discount) <= savings <= float(max_discount)):
                continue

            if max_price is not None and sale_price > float(max_price):
                continue

            if free_only and sale_price != 0:
                continue

            deal_store_id = str(deal.get("storeID"))
            store_name = store_map.get(deal_store_id, f"Store #{deal_store_id}")
            steam_app_id = deal.get("steamAppID")

            all_deals.append({
                "title": deal.get("title"),
                "platform_game_id": str(steam_app_id) if steam_app_id else "",
                "store_id": deal_store_id,
                "store_name": store_name,
                "sale_price": round(sale_price, 2),
                "normal_price": round(normal_price, 2),
                "savings": round(savings, 2),
                "thumb": deal.get("thumb"),
                "steam_app_id": str(steam_app_id) if steam_app_id else "",
                "deal_url": f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}",
                "source": "cheapshark",
            })

            if len(all_deals) >= max_results:
                break

        page_number += 1

    logger.info(f"Fetched {len(all_deals)} deals from CheapShark")
    return all_deals