import requests
BASE_URL="https://www.cheapshark.com/api/1.0"
def fetch_stores():
    r=requests.get(f"{BASE_URL}/stores",timeout=20); r.raise_for_status()
    return [{"store_id":str(s.get("storeID")),"store_name":s.get("storeName")} for s in r.json() if s.get("isActive") in (1,"1")]
def fetch_deals(min_discount=10,max_discount=100,store_id=None,title=None,max_price=None,free_only=False,page_size=60):
    params={"pageSize":page_size,"sortBy":"Savings","desc":"1","lowerPrice":"0","upperPrice":"1000"}
    if store_id: params["storeID"]=store_id
    if title: params["title"]=title
    r=requests.get(f"{BASE_URL}/deals",params=params,timeout=20); r.raise_for_status()
    try: store_map={s["store_id"]:s["store_name"] for s in fetch_stores()}
    except requests.RequestException: store_map={}
    out=[]
    for d in r.json():
        savings=float(d.get("savings",0)); sale=float(d.get("salePrice",0)); normal=float(d.get("normalPrice",0))
        if not(float(min_discount)<=savings<=float(max_discount)): continue
        if max_price is not None and sale>float(max_price): continue
        if free_only and sale!=0: continue
        sid=str(d.get("storeID")); steam=d.get("steamAppID")
        out.append({"title":d.get("title"),"platform_game_id":str(steam) if steam else "","store_id":sid,"store_name":store_map.get(sid,f"Store #{sid}"),"sale_price":sale,"normal_price":normal,"savings":round(savings,2),"thumb":d.get("thumb"),"steam_app_id":str(steam) if steam else "","deal_url":f"https://www.cheapshark.com/redirect?dealID={d.get('dealID')}","source":"cheapshark"})
    return out
