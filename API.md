# API Documentation

Game Deals Assistant provides a clean RESTful API for discovering game discounts, managing personal favorites, setting price alerts, and managing your cross-platform game library.

## Base URL

```
http://localhost:8000
```

## Response Format

All responses are JSON-formatted. Standard HTTP status codes are used:
- `200 OK`: Request succeeded
- `400 Bad Request`: Invalid parameters or validation error
- `404 Not Found`: Resource not found
- `503 Service Unavailable`: External provider API error

---

## 1. System Endpoints

### Health Check
Check API server status and version.

```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "app": "Game Deals Assistant",
  "version": "1.0.0"
}
```

### Current User
Get current profile information (local demo profile).

```http
GET /api/me
```

**Response:**
```json
{
  "id": 1,
  "email": "demo@local"
}
```

---

## 2. Stores & Deals Endpoints

### List Stores
Get featured and active PC game stores.

```http
GET /api/stores
```

**Response:**
```json
{
  "featured": [
    {
      "store_id": "steam_direct",
      "store_name": "Steam Direct",
      "icon_url": null
    },
    {
      "store_id": "cheapshark_all",
      "store_name": "All PC Stores",
      "icon_url": null
    }
  ],
  "all": [
    {
      "store_id": "cheapshark_all",
      "store_name": "All PC Stores",
      "icon_url": null
    },
    {
      "store_id": "1",
      "store_name": "Steam",
      "icon_url": "https://www.cheapshark.com/img/stores/icons/0.png"
    }
  ]
}
```

### Get Deals
Get deals with discounts, sorting, store selection, price caps, and library ownership marks.

```http
GET /api/deals?min_discount=10&max_discount=100&page=0&page_size=60
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_discount` | int | 10 | Minimum discount percentage (0–100) |
| `max_discount` | int | 100 | Maximum discount percentage (0–100) |
| `store_id` | string | null | Filter by specific CheapShark store ID or `steam_direct` |
| `source` | string | null | `steam` or `cheapshark` |
| `title` | string | null | Game title search query |
| `max_price` | float | null | Maximum sale price filter (in USD) |
| `free_only` | boolean | false | Return only 100% free games |
| `hide_owned` | boolean | false | Automatically exclude owned games in your library |
| `page` | int | 0 | Page number (0-indexed) |
| `page_size` | int | 60 | Results per page (1–100) |

**Response:**
```json
{
  "deals": [
    {
      "deal_id": "abcdef12345",
      "title": "The Witcher 3: Wild Hunt",
      "platform_game_id": "292030",
      "store_id": "1",
      "store_name": "Steam",
      "store_icon": "https://www.cheapshark.com/img/stores/icons/0.png",
      "sale_price": 7.99,
      "normal_price": 39.99,
      "savings": 80.0,
      "thumb": "https://cdn.cloudflare.steamstatic.com/steam/apps/292030/capsule_sm_120.jpg",
      "steam_app_id": "292030",
      "deal_url": "https://www.cheapshark.com/redirect?dealID=abcdef12345",
      "source": "cheapshark",
      "steam_rating_percent": 96,
      "steam_rating_text": "Overwhelmingly Positive",
      "metacritic_score": 93,
      "deal_rating": 9.8,
      "owned": false,
      "is_favorite": false
    }
  ],
  "next_page": 1
}
```

---

## 3. Favorites & Price Alerts Endpoints

### List Favorites
```http
GET /api/favorites
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Cyberpunk 2077",
    "store_name": "Steam",
    "deal_url": "https://store.steampowered.com/app/1091500",
    "sale_price": 29.99,
    "normal_price": 59.99,
    "savings": 50.0,
    "target_price": 19.99,
    "created_at": "2026-10-07 10:00:00"
  }
]
```

### Add or Update Favorite
```http
POST /api/favorites
Content-Type: application/json

{
  "title": "Cyberpunk 2077",
  "store_name": "Steam",
  "deal_url": "https://store.steampowered.com/app/1091500",
  "sale_price": 29.99,
  "normal_price": 59.99,
  "savings": 50.0,
  "target_price": 19.99
}
```

### Delete Favorite by ID
```http
DELETE /api/favorites/{favorite_id}
```

### Delete Favorite by Deal URL
```http
POST /api/favorites/delete-by-url
Content-Type: application/json

{
  "deal_url": "https://store.steampowered.com/app/1091500"
}
```

---

## 4. Game Library & Steam Sync Endpoints

### List Owned Games
```http
GET /api/owned-games
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "platform": "steam",
    "platform_game_id": "1091500",
    "title": "Cyberpunk 2077",
    "playtime_minutes": 1540,
    "created_at": "2026-10-07 10:00:00"
  }
]
```

### Add Game Manually
```http
POST /api/owned-games/manual
Content-Type: application/json

{
  "platform": "epic",
  "title": "Grand Theft Auto V",
  "platform_game_id": "gta5-epic",
  "playtime_minutes": 600
}
```

### Delete Game from Library
```http
DELETE /api/owned-games/{owned_game_id}
```

### Sync Steam Library
```http
POST /api/steam/sync
Content-Type: application/json

{
  "steam_id": "76561198000000000"
}
```

**Response:**
```json
{
  "status": "synced",
  "steam_id": "76561198000000000",
  "games_count": 87
}
```
