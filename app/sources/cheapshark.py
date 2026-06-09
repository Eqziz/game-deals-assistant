import requests
BASE_URL="https://www.cheapshark.com/api/1.0"
def fetch_stores():
    r=requests.get(f"{BASE_URL}/stores",timeout=20); r.raise_for_status()
    return [{"store_id":str(s.get("storeID")),"store_name":s.get("storeName")} for s in r.json() if s.get("isActive") in (1,"1")]
def fetch_deals(
    min_discount=10,
    max_discount=100,
    store_id=None,
    title=None,
    max_price=None,
    free_only=False,
    page_size=60,
    max_results=1000
):
    all_deals = []
    page_number = 0

    try:
        stores = fetch_stores()
        store_map = {store["store_id"]: store["store_name"] for store in stores}
    except requests.RequestException:
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

        response = requests.get(f"{BASE_URL}/deals", params=params, timeout=20)
        response.raise_for_status()

        raw_deals = response.json()

        if not raw_deals:
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

            all_deals.append({
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

            if len(all_deals) >= max_results:
                break

        page_number += 1

    return all_deals