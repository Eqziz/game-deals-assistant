# API Documentation

Game Deals Assistant provides a RESTful API for accessing game deals, managing favorites, and managing your library.

## Base URL

```
http://localhost:8000
```

## Authentication

The current version uses a demo user for local development. In production, authentication should be implemented.

## Response Format

All responses are JSON formatted.

### Success Response

```json
{
  "data": [...],
  "status": "success"
}
```

### Error Response

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Endpoints

### 1. Get Stores

Get list of available game stores.

```http
GET /api/stores
```

**Response:**
```json
{
  "featured": [
    {
      "store_id": "steam_direct",
      "store_name": "Steam Direct"
    },
    {
      "store_id": "cheapshark_all",
      "store_name": "All PC Stores"
    }
  ],
  "all": [
    {
      "store_id": "steam_direct",
      "store_name": "Steam Direct"
    },
    {
      "store_id": "1",
      "store_name": "Steam"
    },
    {
      "store_id": "2",
      "store_name": "Amazon"
    }
  ]
}
```

### 2. Get Deals

Get filtered game deals from multiple sources.

```http
GET /api/deals?min_discount=10&max_discount=100&source=steam
```

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `min_discount` | integer | No | 10 | Minimum discount percentage (0-100) |
| `max_discount` | integer | No | 100 | Maximum discount percentage (0-100) |
| `store_id` | string | No | null | Filter by specific store ID |
| `source` | string | No | null | Filter by source: "steam" or "cheapshark" |
| `title` | string | No | null | Search by game title (case-insensitive) |
| `max_price` | number | No | null | Maximum price filter |
| `free_only` | boolean | No | false | Only return free games |
| `hide_owned` | boolean | No | false | Hide games already in your library |

**Response:**
```json
[
  {
    "title": "The Witcher 3: Wild Hunt",
    "platform_game_id": "292030",
    "store_id": "1",
    "store_name": "Steam",
    "sale_price": 19.99,
    "normal_price": 59.99,
    "savings": 66.67,
    "thumb": "https://...",
    "steam_app_id": "292030",
    "deal_url": "https://store.steampowered.com/app/292030",
    "source": "steam",
    "owned": false
  }
]
```

**Status Codes:**
- `200` - Success
- `400` - Invalid discount range
- `503` - API unavailable

### 3. Get Favorites

Get all favorited deals for the user.

```http
GET /api/favorites
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "title": "The Witcher 3: Wild Hunt",
    "store_name": "Steam",
    "deal_url": "https://store.steampowered.com/app/292030",
    "sale_price": 19.99,
    "normal_price": 59.99,
    "savings": 66.67,
    "target_price": 15.00,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### 4. Create Favorite

Add a deal to favorites with optional price alert.

```http
POST /api/favorites
Content-Type: application/json

{
  "title": "The Witcher 3: Wild Hunt",
  "store_name": "Steam",
  "deal_url": "https://store.steampowered.com/app/292030",
  "sale_price": 19.99,
  "normal_price": 59.99,
  "savings": 66.67,
  "target_price": 15.00
}
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Game title (max 500 chars) |
| `store_name` | string | Yes | Store name (max 200 chars) |
| `deal_url` | string | Yes | URL to the deal (max 2000 chars) |
| `sale_price` | number | Yes | Discounted price (≥0) |
| `normal_price` | number | Yes | Original price (≥0) |
| `savings` | number | Yes | Discount percentage (0-100) |
| `target_price` | number | No | Optional price alert threshold (≥0) |

**Response:**
```json
{
  "status": "saved"
}
```

### 5. Delete Favorite

Remove a deal from favorites.

```http
DELETE /api/favorites/{favorite_id}
```

**Parameters:**
- `favorite_id` (integer) - ID of the favorite to delete

**Response:**
```json
{
  "status": "deleted"
}
```

**Status Codes:**
- `200` - Successfully deleted
- `500` - Error deleting favorite

### 6. Get Owned Games

Get all owned games for the user.

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
    "platform_game_id": "292030",
    "title": "The Witcher 3: Wild Hunt",
    "playtime_minutes": 1440,
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### 7. Add Owned Game (Manual)

Manually add a game to your library.

```http
POST /api/owned-games/manual
Content-Type: application/json

{
  "platform": "epic",
  "title": "Elden Ring",
  "platform_game_id": "elden-ring",
  "playtime_minutes": 0
}
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `platform` | string | Yes | Platform name (steam, epic, gog, other) |
| `title` | string | Yes | Game title (max 500 chars) |
| `platform_game_id` | string | No | Platform-specific game ID (max 200 chars) |
| `playtime_minutes` | integer | No | Playtime in minutes (≥0, default: 0) |

**Response:**
```json
{
  "status": "saved"
}
```

**Status Codes:**
- `200` - Success
- `400` - Missing required fields
- `500` - Error adding game

### 8. Delete Owned Game

Remove a game from your library.

```http
DELETE /api/owned-games/{owned_game_id}
```

**Parameters:**
- `owned_game_id` (integer) - ID of the game to remove

**Response:**
```json
{
  "status": "deleted"
}
```

### 9. Get Connected Accounts

Get list of connected platform accounts.

```http
GET /api/accounts
```

**Response:**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "platform": "steam",
    "platform_user_id": "76561198123456789",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

### 10. Sync Steam Library

Synchronize your Steam library by SteamID64.

```http
POST /api/steam/sync
Content-Type: application/json

{
  "steam_id": "76561198123456789"
}
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `steam_id` | string | Yes | 17-digit Steam ID (SteamID64) |

**Response:**
```json
{
  "status": "synced",
  "steam_id": "76561198123456789",
  "games_count": 42
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid or missing Steam ID
- `503` - Steam API unavailable

**Note:** Requires `STEAM_API_KEY` environment variable to be set.

### 11. Get Current User

Get information about the current user.

```http
GET /api/me
```

**Response:**
```json
{
  "id": 1,
  "email": "demo@local",
  "is_premium": 0
}
```

## Error Handling

All errors return appropriate HTTP status codes and include a descriptive error message.

### Common Error Responses

**400 Bad Request**
```json
{
  "detail": "Invalid discount range"
}
```

**404 Not Found**
```json
{
  "detail": "Resource not found"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Internal server error"
}
```

**503 Service Unavailable**
```json
{
  "detail": "Cannot load deals from external API: Connection timeout"
}
```

## Rate Limiting

Currently, there is no rate limiting implemented. This should be added for production deployments.

## Pagination

Pagination is not currently implemented. All results are returned at once, but pagination should be considered for large datasets.

## Caching

Consider implementing caching for:
- Store lists (cached for 24 hours)
- Deals (cached for 1 hour)
- User data (no caching, always fresh)

## Examples

### Get all Steam deals with 50%+ discount

```bash
curl "http://localhost:8000/api/deals?source=steam&min_discount=50&max_discount=100"
```

### Get free games

```bash
curl "http://localhost:8000/api/deals?free_only=true"
```

### Get deals under $10 and hide owned games

```bash
curl "http://localhost:8000/api/deals?max_price=10&hide_owned=true"
```

### Search for Witcher games

```bash
curl "http://localhost:8000/api/deals?title=witcher"
```

### Create a favorite with price alert

```bash
curl -X POST "http://localhost:8000/api/favorites" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cyberpunk 2077",
    "store_name": "Steam",
    "deal_url": "https://store.steampowered.com/app/1091500",
    "sale_price": 29.99,
    "normal_price": 59.99,
    "savings": 50,
    "target_price": 19.99
  }'
```

### Sync Steam library

```bash
curl -X POST "http://localhost:8000/api/steam/sync" \
  -H "Content-Type: application/json" \
  -d '{"steam_id": "76561198123456789"}'
```

## Future Enhancements

- [ ] Token-based authentication
- [ ] Pagination support
- [ ] Rate limiting
- [ ] API versioning
- [ ] Webhooks for price alerts
- [ ] GraphQL endpoint
- [ ] OpenAPI/Swagger documentation UI
