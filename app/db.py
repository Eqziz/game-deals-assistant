"""PostgreSQL persistence. Every write is committed as a unit or rolled back."""

import hashlib
import os
from pathlib import Path
import secrets

import psycopg
from psycopg.rows import dict_row


MIGRATIONS = Path(__file__).with_name("migrations")


def get_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("Set DATABASE_URL to a PostgreSQL connection URL")
    return psycopg.connect(url, connect_timeout=5, row_factory=dict_row)


def init_db():
    migrations = sorted(MIGRATIONS.glob("[0-9][0-9][0-9]_*.sql"))
    with get_connection() as conn:
        # Serialize concurrent startup in the same database.
        conn.execute("SELECT pg_advisory_xact_lock(929045128)")
        conn.execute("""CREATE TABLE IF NOT EXISTS schema_migrations (
            version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now()
        )""")
        applied = {r["version"] for r in conn.execute("SELECT version FROM schema_migrations")}
        if applied - {migration.stem for migration in migrations}:
            raise RuntimeError("The database requires a newer application release")
        for migration in migrations:
            if migration.stem not in applied:
                conn.execute(migration.read_text(encoding="utf-8"))
                conn.execute("INSERT INTO schema_migrations(version) VALUES (%s)", (migration.stem,))


def check_db():
    expected = {migration.stem for migration in MIGRATIONS.glob("*.sql")}
    with get_connection() as conn:
        applied = {r["version"] for r in conn.execute("SELECT version FROM schema_migrations")}
        if applied != expected:
            raise RuntimeError("Database migration required")


def get_or_create_google_user(subject, email, name):
    with get_connection() as conn:
        return conn.execute(
            """INSERT INTO users (google_subject, email, name) VALUES (%s, %s, %s)
               ON CONFLICT (google_subject) DO UPDATE SET email = excluded.email, name = excluded.name
               RETURNING id, email, name""",
            (subject, email, name or ""),
        ).fetchone()


def _digest(token):
    return hashlib.sha256(token.encode("utf-8")).digest()


def create_session(user_id, ttl_seconds=2592000):
    token = secrets.token_urlsafe(32)
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE expires_at <= now()")
        conn.execute(
            """INSERT INTO sessions (token_hash, user_id, expires_at)
               VALUES (%s, %s, now() + make_interval(secs => %s))""",
            (_digest(token), user_id, ttl_seconds),
        )
    return token


def get_session_user(token):
    if not token:
        return None
    with get_connection() as conn:
        return conn.execute(
            """SELECT u.id, u.email, u.name FROM users u JOIN sessions s ON s.user_id = u.id
               WHERE s.token_hash = %s AND s.expires_at > now()""", (_digest(token),)
        ).fetchone()


def delete_session(token):
    if token:
        with get_connection() as conn:
            conn.execute("DELETE FROM sessions WHERE token_hash = %s", (_digest(token),))


def add_favorite(user_id, title, store_name, deal_url, sale_price, normal_price, savings, target_price=None):
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO favorites
               (user_id, title, store_name, deal_url, sale_price, normal_price, savings, target_price)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
               ON CONFLICT (user_id, deal_url) DO UPDATE SET
                   title = excluded.title, store_name = excluded.store_name,
                   sale_price = excluded.sale_price, normal_price = excluded.normal_price,
                   savings = excluded.savings,
                   target_price = coalesce(excluded.target_price, favorites.target_price)""",
            (user_id, title, store_name, deal_url, sale_price, normal_price, savings, target_price),
        )


def list_favorites(user_id):
    with get_connection() as conn:
        return conn.execute(
            """SELECT id, user_id, title, store_name, deal_url, sale_price::float8 AS sale_price,
                      normal_price::float8 AS normal_price, savings::float8 AS savings,
                      target_price::float8 AS target_price, created_at
               FROM favorites WHERE user_id = %s ORDER BY created_at DESC, id DESC""",
            (user_id,),
        ).fetchall()


def favorite_deal_urls(user_id):
    with get_connection() as conn:
        return {row["deal_url"] for row in conn.execute("SELECT deal_url FROM favorites WHERE user_id = %s", (user_id,))}


def delete_favorite(fid, user_id):
    with get_connection() as conn:
        return conn.execute("DELETE FROM favorites WHERE id = %s AND user_id = %s", (fid, user_id)).rowcount > 0


def delete_favorite_by_url(deal_url, user_id):
    with get_connection() as conn:
        return conn.execute("DELETE FROM favorites WHERE deal_url = %s AND user_id = %s", (deal_url, user_id)).rowcount > 0


UPSERT_ACCOUNT = """INSERT INTO connected_accounts (user_id, platform, platform_user_id)
    VALUES (%s, %s, %s) ON CONFLICT (user_id, platform) DO UPDATE SET platform_user_id = excluded.platform_user_id"""

UPSERT_GAME = """INSERT INTO owned_games (user_id, platform, platform_game_id, title, playtime_minutes)
    VALUES (%s, %s, %s, %s, %s) ON CONFLICT (user_id, platform, platform_game_id)
    DO UPDATE SET title = excluded.title, playtime_minutes = excluded.playtime_minutes"""


def list_connected_accounts(user_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM connected_accounts WHERE user_id = %s ORDER BY platform", (user_id,)).fetchall()


def upsert_owned_game(user_id, platform, platform_game_id, title="", playtime_minutes=0):
    with get_connection() as conn:
        conn.execute(UPSERT_GAME, (user_id, platform, str(platform_game_id), title, playtime_minutes))


def save_steam_library(user_id, steam_id, games):
    """Commit the Steam account and its games together on successful import."""
    with get_connection() as conn:
        conn.execute(UPSERT_ACCOUNT, (user_id, "steam", steam_id))
        with conn.cursor() as cur:
            cur.executemany(UPSERT_GAME, [
                (user_id, "steam", str(g["platform_game_id"]), g.get("title") or "", g.get("playtime_minutes") or 0)
                for g in games
            ])


def list_owned_games(user_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM owned_games WHERE user_id = %s ORDER BY platform, title, id", (user_id,)).fetchall()


def delete_owned_game(user_id, owned_game_id):
    with get_connection() as conn:
        return conn.execute("DELETE FROM owned_games WHERE user_id = %s AND id = %s", (user_id, owned_game_id)).rowcount > 0


def owned_game_keys(user_id):
    with get_connection() as conn:
        return {(r["platform"], r["platform_game_id"].lower()) for r in conn.execute(
            "SELECT platform, platform_game_id FROM owned_games WHERE user_id = %s", (user_id,)
        )}


if __name__ == "__main__":
    init_db()
