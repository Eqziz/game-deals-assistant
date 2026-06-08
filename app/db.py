import sqlite3
from pathlib import Path
DB_PATH=Path("game_deals.db")
def get_connection():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
    c=get_connection(); cur=c.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT,email TEXT UNIQUE NOT NULL,is_premium INTEGER NOT NULL DEFAULT 0)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS favorites(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,title TEXT NOT NULL,store_name TEXT NOT NULL,deal_url TEXT NOT NULL,sale_price REAL NOT NULL,normal_price REAL NOT NULL,savings REAL NOT NULL,target_price REAL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS connected_accounts(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,platform TEXT NOT NULL,platform_user_id TEXT NOT NULL,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,UNIQUE(user_id,platform))""")
    cur.execute("""CREATE TABLE IF NOT EXISTS owned_games(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,platform TEXT NOT NULL,platform_game_id TEXT NOT NULL,title TEXT,playtime_minutes INTEGER DEFAULT 0,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,UNIQUE(user_id,platform,platform_game_id))""")
    c.commit(); c.close()
def get_or_create_demo_user():
    c=get_connection(); cur=c.cursor(); cur.execute("SELECT * FROM users WHERE email=?",("demo@local",)); u=cur.fetchone()
    if u is None:
        cur.execute("INSERT INTO users(email,is_premium) VALUES(?,?)",("demo@local",0)); c.commit(); cur.execute("SELECT * FROM users WHERE email=?",("demo@local",)); u=cur.fetchone()
    c.close(); return dict(u)
def set_demo_premium(v):
    c=get_connection(); c.execute("UPDATE users SET is_premium=? WHERE email=?",(1 if v else 0,"demo@local")); c.commit(); c.close()
def add_favorite(user_id,title,store_name,deal_url,sale_price,normal_price,savings,target_price=None):
    c=get_connection(); c.execute("INSERT INTO favorites(user_id,title,store_name,deal_url,sale_price,normal_price,savings,target_price) VALUES(?,?,?,?,?,?,?,?)",(user_id,title,store_name,deal_url,float(sale_price),float(normal_price),float(savings),float(target_price) if target_price is not None else None)); c.commit(); c.close()
def list_favorites(user_id):
    c=get_connection(); rows=[dict(r) for r in c.execute("SELECT * FROM favorites WHERE user_id=? ORDER BY created_at DESC",(user_id,)).fetchall()]; c.close(); return rows
def delete_favorite(fid,user_id):
    c=get_connection(); c.execute("DELETE FROM favorites WHERE id=? AND user_id=?",(fid,user_id)); c.commit(); c.close()
def upsert_connected_account(user_id,platform,platform_user_id):
    c=get_connection(); c.execute("INSERT INTO connected_accounts(user_id,platform,platform_user_id) VALUES(?,?,?) ON CONFLICT(user_id,platform) DO UPDATE SET platform_user_id=excluded.platform_user_id",(user_id,platform,platform_user_id)); c.commit(); c.close()
def list_connected_accounts(user_id):
    c=get_connection(); rows=[dict(r) for r in c.execute("SELECT * FROM connected_accounts WHERE user_id=?",(user_id,)).fetchall()]; c.close(); return rows
def upsert_owned_game(user_id,platform,platform_game_id,title="",playtime_minutes=0):
    c=get_connection(); c.execute("INSERT INTO owned_games(user_id,platform,platform_game_id,title,playtime_minutes) VALUES(?,?,?,?,?) ON CONFLICT(user_id,platform,platform_game_id) DO UPDATE SET title=excluded.title,playtime_minutes=excluded.playtime_minutes",(user_id,platform,str(platform_game_id),title,int(playtime_minutes or 0))); c.commit(); c.close()
def bulk_upsert_owned_games(user_id,games):
    c=get_connection()
    for g in games: c.execute("INSERT INTO owned_games(user_id,platform,platform_game_id,title,playtime_minutes) VALUES(?,?,?,?,?) ON CONFLICT(user_id,platform,platform_game_id) DO UPDATE SET title=excluded.title,playtime_minutes=excluded.playtime_minutes",(user_id,g["platform"],str(g["platform_game_id"]),g.get("title") or "",int(g.get("playtime_minutes") or 0)))
    c.commit(); c.close()
def list_owned_games(user_id):
    c=get_connection(); rows=[dict(r) for r in c.execute("SELECT * FROM owned_games WHERE user_id=? ORDER BY platform,title",(user_id,)).fetchall()]; c.close(); return rows
def delete_owned_game(user_id,owned_game_id):
    c=get_connection(); c.execute("DELETE FROM owned_games WHERE id=? AND user_id=?",(owned_game_id,user_id)); c.commit(); c.close()
def owned_game_keys(user_id):
    return {(g["platform"],str(g["platform_game_id"]).lower()) for g in list_owned_games(user_id) if g.get("platform_game_id")}
