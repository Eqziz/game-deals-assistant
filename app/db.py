import sqlite3
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path("game_deals.db")


def get_connection() -> sqlite3.Connection:
    """Get a database connection"""
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db() -> None:
    """Initialize the database with required tables"""
    c = get_connection()
    cur = c.cursor()
    
    try:
        cur.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            is_premium INTEGER NOT NULL DEFAULT 0
        )""")
        
        cur.execute("""CREATE TABLE IF NOT EXISTS favorites(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            store_name TEXT NOT NULL,
            deal_url TEXT NOT NULL,
            sale_price REAL NOT NULL,
            normal_price REAL NOT NULL,
            savings REAL NOT NULL,
            target_price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        cur.execute("""CREATE TABLE IF NOT EXISTS connected_accounts(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            platform_user_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id,platform)
        )""")
        
        cur.execute("""CREATE TABLE IF NOT EXISTS owned_games(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            platform_game_id TEXT NOT NULL,
            title TEXT,
            playtime_minutes INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id,platform,platform_game_id)
        )""")
        
        c.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        c.close()


def get_or_create_demo_user() -> Dict:
    """Get or create a demo user for local development"""
    c = get_connection()
    cur = c.cursor()
    
    try:
        cur.execute("SELECT * FROM users WHERE email=?", ("demo@local",))
        u = cur.fetchone()
        
        if u is None:
            cur.execute(
                "INSERT INTO users(email,is_premium) VALUES(?,?)",
                ("demo@local", 0)
            )
            c.commit()
            cur.execute("SELECT * FROM users WHERE email=?", ("demo@local",))
            u = cur.fetchone()
        
        return dict(u) if u else {}
    finally:
        c.close()


def set_demo_premium(v: bool) -> None:
    """Set demo user as premium"""
    c = get_connection()
    try:
        c.execute(
            "UPDATE users SET is_premium=? WHERE email=?",
            (1 if v else 0, "demo@local")
        )
        c.commit()
    finally:
        c.close()


def add_favorite(
    user_id: int, title: str, store_name: str, deal_url: str,
    sale_price: float, normal_price: float, savings: float,
    target_price: float = None
) -> None:
    """Add a deal to user's favorites"""
    c = get_connection()
    try:
        c.execute(
            """INSERT INTO favorites(
                user_id, title, store_name, deal_url, sale_price,
                normal_price, savings, target_price
            ) VALUES(?,?,?,?,?,?,?,?)""",
            (user_id, title, store_name, deal_url, float(sale_price),
             float(normal_price), float(savings),
             float(target_price) if target_price is not None else None)
        )
        c.commit()
    finally:
        c.close()


def list_favorites(user_id: int) -> List[Dict]:
    """Get all favorites for a user"""
    c = get_connection()
    try:
        rows = [
            dict(r) for r in c.execute(
                "SELECT * FROM favorites WHERE user_id=? ORDER BY created_at DESC",
                (user_id,)
            ).fetchall()
        ]
        return rows
    finally:
        c.close()


def delete_favorite(fid: int, user_id: int) -> bool:
    """Delete a favorite. Returns True if a row was actually deleted."""
    c = get_connection()
    try:
        cur = c.cursor()
        cur.execute(
            "DELETE FROM favorites WHERE id=? AND user_id=?",
            (fid, user_id)
        )
        c.commit()
        return cur.rowcount > 0
    finally:
        c.close()


def upsert_connected_account(user_id: int, platform: str, platform_user_id: str) -> None:
    """Create or update a connected account"""
    c = get_connection()
    try:
        c.execute(
            """INSERT INTO connected_accounts(user_id,platform,platform_user_id)
               VALUES(?,?,?)
               ON CONFLICT(user_id,platform)
               DO UPDATE SET platform_user_id=excluded.platform_user_id""",
            (user_id, platform, platform_user_id)
        )
        c.commit()
    finally:
        c.close()


def list_connected_accounts(user_id: int) -> List[Dict]:
    """Get all connected accounts for a user"""
    c = get_connection()
    try:
        rows = [
            dict(r) for r in c.execute(
                "SELECT * FROM connected_accounts WHERE user_id=?",
                (user_id,)
            ).fetchall()
        ]
        return rows
    finally:
        c.close()


def upsert_owned_game(
    user_id: int, platform: str, platform_game_id: str,
    title: str = "", playtime_minutes: int = 0
) -> None:
    """Create or update an owned game entry"""
    c = get_connection()
    try:
        c.execute(
            """INSERT INTO owned_games(user_id,platform,platform_game_id,title,playtime_minutes)
               VALUES(?,?,?,?,?)
               ON CONFLICT(user_id,platform,platform_game_id)
               DO UPDATE SET title=excluded.title,playtime_minutes=excluded.playtime_minutes""",
            (user_id, platform, str(platform_game_id), title, int(playtime_minutes or 0))
        )
        c.commit()
    finally:
        c.close()


def bulk_upsert_owned_games(user_id: int, games: List[Dict]) -> None:
    """Bulk insert or update owned games"""
    c = get_connection()
    try:
        for g in games:
            c.execute(
                """INSERT INTO owned_games(user_id,platform,platform_game_id,title,playtime_minutes)
                   VALUES(?,?,?,?,?)
                   ON CONFLICT(user_id,platform,platform_game_id)
                   DO UPDATE SET title=excluded.title,playtime_minutes=excluded.playtime_minutes""",
                (user_id, g["platform"], str(g["platform_game_id"]),
                 g.get("title") or "", int(g.get("playtime_minutes") or 0))
            )
        c.commit()
    finally:
        c.close()


def list_owned_games(user_id: int) -> List[Dict]:
    """Get all owned games for a user"""
    c = get_connection()
    try:
        rows = [
            dict(r) for r in c.execute(
                "SELECT * FROM owned_games WHERE user_id=? ORDER BY platform,title",
                (user_id,)
            ).fetchall()
        ]
        return rows
    finally:
        c.close()


def delete_owned_game(user_id: int, owned_game_id: int) -> bool:
    """Delete an owned game entry. Returns True if a row was actually deleted."""
    c = get_connection()
    try:
        cur = c.cursor()
        cur.execute(
            "DELETE FROM owned_games WHERE id=? AND user_id=?",
            (owned_game_id, user_id)
        )
        c.commit()
        return cur.rowcount > 0
    finally:
        c.close()


def owned_game_keys(user_id: int) -> Set[Tuple[str, str]]:
    """Get set of (platform, game_id) tuples for quick lookup"""
    return {
        (g["platform"], str(g["platform_game_id"]).lower())
        for g in list_owned_games(user_id)
        if g.get("platform_game_id")
    }