"""Direct GOG.com Store Catalog API integration."""

import logging
import re
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

GOG_CATALOG_URL = "https://catalog.gog.com/v1/catalog"
GOG_MAX_LIMIT = 48
HEADERS = {
    "User-Agent": "GameDealsAssistant/1.0 (+https://github.com/Eqziz/game-deals-assistant)",
    "Accept": "application/json",
}


def _parse_money(value) -> Optional[float]:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _parse_discount(discount_str: Optional[str], sale_price: float, normal_price: float) -> float:
    if discount_str:
        match = re.search(r"(\d+)", str(discount_str))
        if match:
            return float(match.group(1))
    if normal_price > sale_price >= 0:
        return round((1 - sale_price / normal_price) * 100, 2)
    return 0.0


def fetch_gog_deals(
    min_discount: int = 10,
    max_discount: int = 100,
    title: Optional[str] = None,
    max_price: Optional[float] = None,
    free_only: bool = False,
    page: int = 0,
    page_size: int = 48,
) -> Dict:
    """Fetch discounted games directly from GOG's public catalog API."""
    limit = min(max(1, page_size), GOG_MAX_LIMIT)
    gog_page = max(0, page) + 1

    params: Dict[str, str | int] = {
        "limit": limit,
        "page": gog_page,
        "discounted": "eq:true",
        "order": "desc:bestselling",
        "productType": "in:game,pack",
        "countryCode": "US",
        "currencyCode": "USD",
        "locale": "en-US",
    }

    if title:
        params["query"] = f"like:{title.strip()}"

    if free_only:
        params["price"] = "between:0,0"
    elif max_price is not None:
        params["price"] = f"between:0,{float(max_price):.2f}"

    try:
        response = requests.get(GOG_CATALOG_URL, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as error:
        logger.warning("GOG catalog unavailable (%s)", type(error).__name__)
        raise

    products = data.get("products") or []
    total_pages = int(data.get("pages") or 0)
    results: List[Dict] = []

    for product in products:
        price_info = product.get("price") or {}
        final_money = price_info.get("finalMoney") or {}
        base_money = price_info.get("baseMoney") or {}

        sale_price = _parse_money(final_money.get("amount"))
        normal_price = _parse_money(base_money.get("amount"))

        if sale_price is None:
            continue
        if normal_price is None or normal_price < sale_price:
            normal_price = sale_price

        savings = _parse_discount(price_info.get("discount"), sale_price, normal_price)

        if not (float(min_discount) <= savings <= float(max_discount)):
            continue
        if max_price is not None and sale_price > float(max_price):
            continue
        if free_only and sale_price != 0:
            continue

        game_title = product.get("title") or "Unknown game"
        if title and title.strip().lower() not in game_title.lower():
            continue

        slug = product.get("slug") or ""
        deal_url = product.get("storeLink") or (f"https://www.gog.com/en/game/{slug}" if slug else "https://www.gog.com")
        thumb = product.get("coverHorizontal") or product.get("coverVertical") or ""

        reviews_rating = product.get("reviewsRating")
        deal_rating = round(float(reviews_rating) / 5.0, 1) if reviews_rating else None

        results.append({
            "title": game_title,
            "platform_game_id": str(product.get("id") or ""),
            "store_id": "gog",
            "store_name": "GOG",
            "store_icon": None,
            "sale_price": sale_price,
            "normal_price": normal_price,
            "savings": round(savings, 2),
            "thumb": thumb,
            "steam_app_id": "",
            "deal_url": deal_url,
            "source": "gog",
            "steam_rating_percent": None,
            "steam_rating_text": None,
            "metacritic_score": None,
            "deal_rating": deal_rating,
        })

    next_page = page + 1 if gog_page < total_pages else None
    logger.info("Fetched %d GOG deals for page %d", len(results), page)
    return {
        "deals": results,
        "next_page": next_page,
    }
