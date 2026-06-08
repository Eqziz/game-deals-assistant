import os
import requests
STEAM_FEATURED_URL = "https://store.steampowered.com/api/featuredcategories"
STEAM_OWNED_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"

def cents_to_money(value):
    try: return round(float(value)/100,2)
    except (TypeError,ValueError): return 0.0

def fetch_steam_specials(min_discount=10,max_discount=100,title=None,max_price=None,free_only=False,cc="us",language="english"):
    r=requests.get(STEAM_FEATURED_URL,params={"cc":cc,"l":language},timeout=20); r.raise_for_status()
    specials=r.json().get("specials",{}).get("items",[])
    out=[]
    for item in specials:
        discount=int(item.get("discount_percent") or 0)
        if discount<min_discount or discount>max_discount: continue
        app_id=item.get("id"); game_title=item.get("name") or "Unknown game"
        if title and title.lower() not in game_title.lower(): continue
        final_price=cents_to_money(item.get("final_price")); normal_price=cents_to_money(item.get("original_price"))
        if normal_price<=0 and final_price>0 and discount>0: normal_price=round(final_price/(1-discount/100),2)
        if max_price is not None and final_price>float(max_price): continue
        if free_only and final_price!=0: continue
        out.append({"title":game_title,"platform_game_id":str(app_id),"store_id":"steam","store_name":"Steam","sale_price":final_price,"normal_price":normal_price,"savings":discount,"thumb":item.get("large_capsule_image") or item.get("small_capsule_image") or "","steam_app_id":str(app_id),"deal_url":f"https://store.steampowered.com/app/{app_id}","source":"steam"})
    return out

def fetch_owned_steam_games(steam_id,api_key=None):
    api_key=api_key or os.getenv("STEAM_API_KEY")
    if not api_key: raise ValueError("STEAM_API_KEY is not set.")
    params={"key":api_key,"steamid":steam_id,"format":"json","include_appinfo":1,"include_played_free_games":1}
    r=requests.get(STEAM_OWNED_GAMES_URL,params=params,timeout=25); r.raise_for_status()
    games=r.json().get("response",{}).get("games",[])
    return [{"platform":"steam","platform_game_id":str(g.get("appid")),"title":g.get("name") or "","playtime_minutes":int(g.get("playtime_forever") or 0)} for g in games]
