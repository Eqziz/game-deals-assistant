from fastapi import FastAPI,HTTPException,Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from .db import *
from .sources.steam import fetch_steam_specials,fetch_owned_steam_games
from .sources.cheapshark import fetch_deals as fetch_cheapshark_deals, fetch_stores
app=FastAPI(title="Game Deals Assistant")
app.mount("/static",StaticFiles(directory="app/static"),name="static")
class FavoriteCreate(BaseModel):
    title:str; store_name:str; deal_url:str; sale_price:float; normal_price:float; savings:float; target_price:float|None=None

class ManualOwnedGameCreate(BaseModel):
    platform:str; platform_game_id:str|None=None; title:str; playtime_minutes:int=0
class SteamSyncRequest(BaseModel): steam_id:str
@app.on_event("startup")
def startup(): init_db(); get_or_create_demo_user()
@app.get("/")
def index(): return FileResponse("app/static/index.html")
@app.get("/api/me")
def me(): return get_or_create_demo_user()

@app.get("/api/stores")
def stores():
    result=[{"store_id":"steam_direct","store_name":"Steam Direct"},{"store_id":"cheapshark_all","store_name":"All PC Stores"}]
    try: cs=fetch_stores()
    except requests.RequestException: cs=[]
    return {"featured":result,"all":result+cs}
def mark_owned(deals,user_id,hide_owned=False):
    keys=owned_game_keys(user_id); titles={(g.get("title") or "").strip().lower() for g in list_owned_games(user_id) if g.get("title")}
    out=[]
    for d in deals:
        store=(d.get("store_name") or "").lower(); platform="steam" if "steam" in store or d.get("source")=="steam" else "unknown"
        gid=str(d.get("platform_game_id") or d.get("steam_app_id") or "").lower(); title=(d.get("title") or "").strip().lower()
        owned=(gid and (platform,gid) in keys) or (title and title in titles)
        d["owned"]=bool(owned)
        if hide_owned and owned: continue
        out.append(d)
    return out
@app.get("/api/deals")
def deals(min_discount:int=10,max_discount:int=100,store_id:str|None=None,title:str|None=None,max_price:float|None=Query(default=None),free_only:bool=False,source:str|None=None,hide_owned:bool=False):
    if min_discount<0 or max_discount>100 or min_discount>max_discount: raise HTTPException(status_code=400,detail="Invalid discount range.")
    user=get_or_create_demo_user()
    try:
        if source=="steam" or store_id=="steam_direct": loaded=fetch_steam_specials(min_discount,max_discount,title,max_price,free_only,cc="us",language="english")
        else:
            real=None if store_id in (None,"","cheapshark_all") else store_id
            loaded=fetch_cheapshark_deals(min_discount,max_discount,real,title,max_price,free_only)
        return mark_owned(loaded,user["id"],hide_owned)
    except requests.RequestException as e: raise HTTPException(status_code=503,detail=f"Cannot load deals from external API: {e}")
@app.post("/api/favorites")
def favorite_create(p:FavoriteCreate):
    u=get_or_create_demo_user(); add_favorite(u["id"],p.title,p.store_name,p.deal_url,p.sale_price,p.normal_price,p.savings,p.target_price); return {"status":"saved"}
@app.get("/api/favorites")
def favorite_list(): u=get_or_create_demo_user(); return list_favorites(u["id"])
@app.delete("/api/favorites/{favorite_id}")
def favorite_delete(favorite_id:int): u=get_or_create_demo_user(); delete_favorite(favorite_id,u["id"]); return {"status":"deleted"}
@app.get("/api/accounts")
def accounts(): u=get_or_create_demo_user(); return list_connected_accounts(u["id"])
@app.get("/api/owned-games")
def owned_games(): u=get_or_create_demo_user(); return list_owned_games(u["id"])
@app.post("/api/owned-games/manual")
def add_owned_game_manual(p:ManualOwnedGameCreate):
    u=get_or_create_demo_user(); platform=p.platform.strip().lower(); title=p.title.strip()
    if not platform or not title: raise HTTPException(status_code=400,detail="Platform and title are required.")
    gid=p.platform_game_id.strip() if p.platform_game_id else title.lower()
    upsert_owned_game(u["id"],platform,gid,title,p.playtime_minutes); return {"status":"saved"}
@app.delete("/api/owned-games/{owned_game_id}")
def remove_owned_game(owned_game_id:int): u=get_or_create_demo_user(); delete_owned_game(u["id"],owned_game_id); return {"status":"deleted"}
@app.post("/api/steam/sync")
def sync_steam_library(p:SteamSyncRequest):
    u=get_or_create_demo_user(); sid=p.steam_id.strip()
    if not sid: raise HTTPException(status_code=400,detail="SteamID64 is required.")
    try: games=fetch_owned_steam_games(sid)
    except ValueError as e: raise HTTPException(status_code=400,detail=str(e))
    except requests.RequestException as e: raise HTTPException(status_code=503,detail=f"Steam API error: {e}")
    upsert_connected_account(u["id"],"steam",sid); bulk_upsert_owned_games(u["id"],games)
    return {"status":"synced","steam_id":sid,"games_count":len(games)}

