import requests

BASE_URL = "https://www.cheapshark.com/api/1.0"


def fetch_stores():
    response = requests.get(f"{BASE_URL}/stores", timeout=20)
    response.raise_for_status()

    stores = response.json()
    active_stores = []

    for store in stores:
        is_active = store.get("isActive")

        if is_active == 1 or is_active == "1":
            active_stores.append({
                "store_id": str(store.get("storeID")),
                "store_name": store.get("storeName"),
            })

    return active_stores


def fetch_deals(
    min_discount=10,
    max_discount=100,
    store_id=None,
    title=None,
    max_price=None,
    free_only=False,
    page_size=60,
    page_number=0,
    max_scan_pages=5
):
    try:
        stores = fetch_stores()
        store_map = {store["store_id"]: store["store_name"] for store in stores}
    except requests.RequestException:
        store_map = {}

    result = []
    current_page = page_number
    scanned_pages = 0
    next_page = None

    while scanned_pages < max_scan_pages:
        params = {
            "pageSize": page_size,
            "pageNumber": current_page,
            "sortBy": "Savings",
            "desc": "1",
            "lowerPrice": "0",
            "upperPrice": "1000",
        }

        if store_id:
            params["storeID"] = store_id

        if title:
            params["title"] = title

        response = requests.get(f"{BASE_URL}/deals", params=params, timeout=20)
        response.raise_for_status()

        raw_deals = response.json()

        if not raw_deals:
            next_page = None
            break

        for deal in raw_deals:
            savings = float(deal.get("savings", 0))
            sale_price = float(deal.get("salePrice", 0))
            normal_price = float(deal.get("normalPrice", 0))

            if not (float(min_discount) <= savings <= float(max_discount)):
                continue

            if max_price is not None and sale_price > float(max_price):
                continue

            if free_only and sale_price != 0:
                continue

            deal_store_id = str(deal.get("storeID"))
            store_name = store_map.get(deal_store_id, f"Store #{deal_store_id}")
            steam_app_id = deal.get("steamAppID")

            result.append({
                "title": deal.get("title"),
                "platform_game_id": str(steam_app_id) if steam_app_id else "",
                "store_id": deal_store_id,
                "store_name": store_name,
                "sale_price": sale_price,
                "normal_price": normal_price,
                "savings": round(savings, 2),
                "thumb": deal.get("thumb"),
                "steam_app_id": str(steam_app_id) if steam_app_id else "",
                "deal_url": f"https://www.cheapshark.com/redirect?dealID={deal.get('dealID')}",
                "source": "cheapshark",
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