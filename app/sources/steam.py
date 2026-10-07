import logging
import os
import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import requests

logger = logging.getLogger(__name__)

STEAM_SEARCH_URL = "https://store.steampowered.com/search/results/"
STEAM_FEATURED_URL = "https://store.steampowered.com/api/featuredcategories"
STEAM_OWNED_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
STEAM_ICON_URL = "https://www.cheapshark.com/img/stores/icons/0.png"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def cents_to_money(value) -> float:
    """Convert cents to money (dollars)."""
    try:
        return round(float(value) / 100, 2)
    except (TypeError, ValueError):
        return 0.0


def parse_price(txt: str) -> float:
    """Parse price string like '$19.99' or 'Free' to float."""
    if not txt:
        return 0.0
    cleaned = txt.replace("Free", "0").replace("$", "").replace("USD", "").replace(",", ".").strip()
    try:
        return round(float(cleaned), 2)
    except (ValueError, TypeError):
        return 0.0


def fetch_steam_deals(
    min_discount: int = 10,
    max_discount: int = 100,
    title: Optional[str] = None,
    max_price: Optional[float] = None,
    free_only: bool = False,
    page: int = 0,
    page_size: int = 60,
    cc: str = "us",
    language: str = "english",
) -> Dict:
    """
    Fetch deals directly from Steam Store Search with full catalog pagination.
    Supports 60 games per page across all Steam specials.
    """
    start = max(0, page) * page_size
    params = {
        "specials": "1",
        "start": start,
        "count": page_size,
        "cc": cc,
        "l": language,
    }

    if title:
        params["term"] = title.strip()

    if free_only:
        params["maxprice"] = "free"
    elif max_price is not None:
        params["maxprice"] = str(int(max_price))

    try:
        response = requests.get(STEAM_SEARCH_URL, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()
    except requests.RequestException as error:
        logger.error(f"Error requesting Steam Store search: {error}")
        # Fall back to featured specials if search fails
        fallback_specials = fetch_steam_specials(
            min_discount=min_discount,
            max_discount=max_discount,
            title=title,
            max_price=max_price,
            free_only=free_only,
            cc=cc,
            language=language,
        )
        return {
            "deals": fallback_specials,
            "next_page": None,
        }

    soup = BeautifulSoup(response.text, "html.parser")
    rows = soup.select("a.search_result_row")

    results: List[Dict] = []

    for row in rows:
        title_el = row.select_one(".title")
        discount_el = row.select_one(".discount_pct")
        price_orig_el = row.select_one(".discount_original_price")
        price_final_el = row.select_one(".discount_final_price")
        img_el = row.select_one(".search_capsule img")
        raw_appid = row.get("data-ds-appid") or ""
        href = row.get("href") or ""

        game_title = title_el.text.strip() if title_el else "Unknown game"

        # Filter by title if user specified
        if title and title.lower() not in game_title.lower():
            continue

        discount_text = discount_el.text.strip() if discount_el else ""
        m_disc = re.search(r"(\d+)", discount_text)
        discount = int(m_disc.group(1)) if m_disc else 0

        orig_price = parse_price(price_orig_el.text if price_orig_el else "")
        sale_price = parse_price(price_final_el.text if price_final_el else "")

        if discount == 0 and orig_price > sale_price > 0:
            discount = int(round((1 - sale_price / orig_price) * 100))

        if not (min_discount <= discount <= max_discount):
            continue

        if max_price is not None and sale_price > float(max_price):
            continue

        if free_only and sale_price != 0:
            continue

        # Extract primary appid
        appid = raw_appid.split(",")[0].strip() if raw_appid else ""

        # High quality thumbnail fallback
        thumb = img_el.get("src") if img_el else ""
        if not thumb and appid:
            thumb = f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/capsule_231x87.jpg"

        # Rating info
        steam_rating_text = None
        steam_rating_percent = None
        review_el = row.select_one(".search_review_summary")
        if review_el:
            tooltip = review_el.get("data-tooltip-html") or ""
            if tooltip:
                parts = tooltip.split("<br>")
                steam_rating_text = parts[0].strip() if parts else None
                m_rev = re.search(r"(\d+)%", tooltip)
                if m_rev:
                    steam_rating_percent = int(m_rev.group(1))

        clean_url = href.split("?")[0] if href else f"https://store.steampowered.com/app/{appid}"

        results.append({
            "title": game_title,
            "platform_game_id": str(appid),
            "store_id": "steam",
            "store_name": "Steam",
            "store_icon": STEAM_ICON_URL,
            "sale_price": sale_price,
            "normal_price": orig_price if orig_price > 0 else sale_price,
            "savings": discount,
            "thumb": thumb,
            "steam_app_id": str(appid),
            "deal_url": clean_url,
            "source": "steam",
            "steam_rating_percent": steam_rating_percent,
            "steam_rating_text": steam_rating_text,
            "metacritic_score": None,
            "deal_rating": None,
        })

    has_more = len(rows) == page_size
    next_page = page + 1 if has_more else None

    logger.info(f"Fetched {len(results)} Steam Store deals for page {page}")
    return {
        "deals": results,
        "next_page": next_page,
    }


def fetch_steam_specials(
    min_discount: int = 10,
    max_discount: int = 100,
    title: Optional[str] = None,
    max_price: Optional[float] = None,
    free_only: bool = False,
    cc: str = "us",
    language: str = "english",
) -> List[Dict]:
    """Fetch featured specials from Steam Store API (fallback)."""
    try:
        r = requests.get(
            STEAM_FEATURED_URL,
            params={"cc": cc, "l": language},
            headers=HEADERS,
            timeout=20,
        )
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching Steam specials: {e}")
        return []

    specials = r.json().get("specials", {}).get("items", [])
    out = []

    for item in specials:
        discount = int(item.get("discount_percent") or 0)
        if discount < min_discount or discount > max_discount:
            continue

        app_id = item.get("id")
        game_title = item.get("name") or "Unknown game"

        if title and title.lower() not in game_title.lower():
            continue

        final_price = cents_to_money(item.get("final_price"))
        normal_price = cents_to_money(item.get("original_price"))

        if normal_price <= 0 and final_price > 0 and discount > 0:
            normal_price = round(final_price / (1 - discount / 100), 2)

        if max_price is not None and final_price > float(max_price):
            continue

        if free_only and final_price != 0:
            continue

        out.append({
            "title": game_title,
            "platform_game_id": str(app_id),
            "store_id": "steam",
            "store_name": "Steam",
            "store_icon": STEAM_ICON_URL,
            "sale_price": final_price,
            "normal_price": normal_price,
            "savings": discount,
            "thumb": item.get("large_capsule_image") or item.get("small_capsule_image") or "",
            "steam_app_id": str(app_id),
            "deal_url": f"https://store.steampowered.com/app/{app_id}",
            "source": "steam",
            "steam_rating_percent": None,
            "steam_rating_text": None,
            "metacritic_score": None,
            "deal_rating": None,
        })

    return out


def fetch_owned_steam_games(steam_id: str, api_key: Optional[str] = None) -> List[Dict]:
    """Fetch owned games from Steam Web API."""
    api_key = api_key or os.getenv("STEAM_API_KEY")

    if not api_key:
        logger.error("STEAM_API_KEY is not set")
        raise ValueError("STEAM_API_KEY is not set. Please set it in your environment variables.")

    params = {
        "key": api_key,
        "steamid": steam_id,
        "format": "json",
        "include_appinfo": 1,
        "include_played_free_games": 1,
    }

    try:
        r = requests.get(STEAM_OWNED_GAMES_URL, params=params, headers=HEADERS, timeout=25)
        r.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Error fetching Steam owned games: {e}")
        raise

    response_data = r.json()
    games = response_data.get("response", {}).get("games", [])

    result = [
        {
            "platform": "steam",
            "platform_game_id": str(g.get("appid")),
            "title": g.get("name") or "",
            "playtime_minutes": int(g.get("playtime_forever") or 0),
        }
        for g in games
    ]

    logger.info(f"Fetched {len(result)} owned games from Steam")
    return result
