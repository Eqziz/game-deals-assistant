"""Direct Epic Games Store API integration."""

import logging
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)

EPIC_GRAPHQL_URL = "https://store.epicgames.com/graphql"
EPIC_PROMOS_URL = "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
}

EPIC_SEARCH_QUERY = """
query searchStoreQuery($count: Int, $start: Int, $onSale: Boolean, $keywords: String, $country: String!, $locale: String!) {
  Catalog {
    searchStore(count: $count, start: $start, onSale: $onSale, keywords: $keywords, country: $country, locale: $locale, category: "games/edition/base") {
      elements {
        title
        id
        productSlug
        urlSlug
        catalogNs {
          mappings(pageType: "productHome") {
            pageSlug
          }
        }
        keyImages {
          type
          url
        }
        price(country: $country) {
          totalPrice {
            discountPrice
            originalPrice
            discount
            currencyInfo {
              decimals
            }
          }
        }
      }
      paging {
        count
        total
      }
    }
  }
}
"""


def _extract_thumb(key_images: List[Dict]) -> str:
    preferred = ("OfferImageWide", "DieselStoreFrontWide", "Thumbnail", "OfferImageTall")
    by_type = {img.get("type"): img.get("url") for img in (key_images or []) if img.get("url")}
    for kind in preferred:
        if kind in by_type:
            return by_type[kind]
    return next(iter(by_type.values()), "")


def _extract_url(element: Dict) -> str:
    mappings = (element.get("catalogNs") or {}).get("mappings") or []
    slug = (
        (mappings[0].get("pageSlug") if mappings else None)
        or element.get("productSlug")
        or element.get("urlSlug")
        or ""
    ).split("/")[0]
    if slug:
        return f"https://store.epicgames.com/en-US/p/{slug}"
    return "https://store.epicgames.com/en-US/browse"


def _parse_elements(
    elements: List[Dict],
    min_discount: int,
    max_discount: int,
    title: Optional[str],
    max_price: Optional[float],
    free_only: bool,
) -> List[Dict]:
    results: List[Dict] = []
    seen_urls = set()

    for elem in elements:
        game_title = elem.get("title") or "Unknown game"
        if title and title.strip().lower() not in game_title.lower():
            continue

        total_price = (elem.get("price") or {}).get("totalPrice") or {}
        decimals = int((total_price.get("currencyInfo") or {}).get("decimals", 2))
        divisor = 10 ** decimals

        try:
            orig_raw = int(total_price.get("originalPrice") or 0)
            sale_raw = int(total_price.get("discountPrice") or 0)
        except (TypeError, ValueError):
            continue

        normal_price = round(orig_raw / divisor, 2)
        sale_price = round(sale_raw / divisor, 2)

        if normal_price <= 0 and sale_price <= 0:
            # Free-to-play base game without discount unless explicitly free_only
            if not free_only:
                continue
            savings = 0.0
        elif normal_price > sale_price >= 0:
            savings = round((1 - sale_price / normal_price) * 100, 2)
        else:
            savings = 0.0

        if not (float(min_discount) <= savings <= float(max_discount)):
            continue
        if max_price is not None and sale_price > float(max_price):
            continue
        if free_only and sale_price != 0:
            continue

        deal_url = _extract_url(elem)
        if deal_url in seen_urls:
            continue
        seen_urls.add(deal_url)

        results.append({
            "title": game_title,
            "platform_game_id": str(elem.get("id") or ""),
            "store_id": "epic",
            "store_name": "Epic Games Store",
            "store_icon": None,
            "sale_price": sale_price,
            "normal_price": normal_price if normal_price > 0 else sale_price,
            "savings": round(savings, 2),
            "thumb": _extract_thumb(elem.get("keyImages") or []),
            "steam_app_id": "",
            "deal_url": deal_url,
            "source": "epic",
            "steam_rating_percent": None,
            "steam_rating_text": None,
            "metacritic_score": None,
            "deal_rating": None,
        })

    return results


def _fetch_free_promotions() -> List[Dict]:
    response = requests.get(
        EPIC_PROMOS_URL,
        params={"locale": "en-US", "country": "US", "allowCountries": "US"},
        headers={"User-Agent": HEADERS["User-Agent"], "Accept": "application/json"},
        timeout=15,
    )
    response.raise_for_status()
    return (
        response.json()
        .get("data", {})
        .get("Catalog", {})
        .get("searchStore", {})
        .get("elements", [])
    )


def fetch_epic_deals(
    min_discount: int = 10,
    max_discount: int = 100,
    title: Optional[str] = None,
    max_price: Optional[float] = None,
    free_only: bool = False,
    page: int = 0,
    page_size: int = 40,
) -> Dict:
    """Fetch discounted and free promotional games directly from Epic Games Store."""
    limit = min(max(1, page_size), 40)
    start = max(0, page) * limit

    try:
        variables = {
            "count": limit,
            "start": start,
            "onSale": not free_only,
            "keywords": title.strip() if title else "",
            "country": "US",
            "locale": "en-US",
        }
        response = requests.post(
            EPIC_GRAPHQL_URL,
            json={"query": EPIC_SEARCH_QUERY, "variables": variables},
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        search_store = (payload.get("data") or {}).get("Catalog", {}).get("searchStore")
        if not search_store:
            raise requests.RequestException("Empty Epic GraphQL response")

        elements = list(search_store.get("elements") or [])
        total = int((search_store.get("paging") or {}).get("total") or 0)

        # Include current weekly free promotions on the first page.
        if page == 0 and (free_only or max_discount == 100):
            try:
                elements = _fetch_free_promotions() + elements
            except requests.RequestException:
                pass

        deals = _parse_elements(elements, min_discount, max_discount, title, max_price, free_only)
        next_page = page + 1 if (start + limit) < total else None
        logger.info("Fetched %d Epic deals for page %d", len(deals), page)
        return {"deals": deals, "next_page": next_page}

    except requests.RequestException as error:
        if page == 0:
            try:
                promo_elements = _fetch_free_promotions()
                deals = _parse_elements(promo_elements, min_discount, max_discount, title, max_price, free_only)
                return {"deals": deals, "next_page": None}
            except requests.RequestException:
                pass
        logger.warning("Epic Games Store unavailable (%s)", type(error).__name__)
        raise
