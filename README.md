# Game Deals Assistant

**Game Deals Assistant** is a personal web application for tracking game discounts across multiple platforms (Steam, CheapShark), saving favorite deals, managing your game library, and marking games you already own.

Built with modern web technologies: **FastAPI**, **SQLite**, **HTML/CSS/JavaScript**, and **Docker**.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

##  Features

### Deal Discovery
-  **Steam Store Integration** - View real-time Steam discounts
-  **CheapShark Support** - Access deals from 100+ PC game stores
-  **Advanced Filtering** - Filter by discount percentage, price range, store
-  **Game Search** - Search deals by game title
-  **Smart Sorting** - Sort by discount, price, title, or store
-  **Preset Filters** - Quick access to 90%+, 75%+, Under $5, Free games

### Library Management
-  **Manual Library** - Add owned games from any platform (Steam, Epic, GOG, etc.)
-  **Steam Library Sync** - Auto-sync your Steam library via SteamID64
-  **Hide Owned Games** - Automatically hide already-owned games from deals
-  **Playtime Tracking** - See playtime hours for Steam-synced games

### Favorites & Preferences
-  **Save Favorites** - Add deals to your favorites list
-  **Price Alerts** - Set target prices for deals you're watching
-  **Language Support** - English/Russian UI with persistent preferences
-  **Local Storage** - All data stored locally in SQLite

##  Quick Start

### Prerequisites
- Python 3.12+
- pip or conda
- Optional: Steam API Key (for Steam library sync)

### Installation

#### Option 1: Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Eqziz/game-deals-assistant.git
   cd game_deals_assistant
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   
   # macOS/Linux
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (Optional)
   ```bash
   cp .env.example .env
   # Edit .env and add your Steam API key if you have one
   ```

5. **Run the application**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

6. **Open in browser**
   ```
   http://127.0.0.1:8000
   ```

#### Option 2: Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **Open in browser**
   ```
   http://localhost:8000
   ```

3. **Stop the container**
   ```bash
   docker-compose down
   ```

##  Steam API Setup (Optional)

Steam Library Sync requires a Steam Web API key. Without it, you can still manually add owned games.

### Get Your Steam API Key

1. Go to https://steamcommunity.com/dev/apikey
2. Accept the agreement and enter a domain (e.g., `localhost`)
3. Copy your API key

### Set Environment Variable

**Windows (PowerShell)**
```powershell
$env:STEAM_API_KEY="your_api_key_here"
uvicorn app.main:app --reload
```

**macOS/Linux (Bash)**
```bash
export STEAM_API_KEY="your_api_key_here"
python -m uvicorn app.main:app --reload
```

##  Usage Guide

### Finding Deals
1. Select filters (discount %, source, search term)
2. Click **"Find Deals"** or use preset buttons
3. Click **"Open"** to view deal or **"Add to Favorites"** to save

### Steam Library Sync
1. Find your SteamID64 (17-digit number from Steam profile)
2. Enter it in "Connect Steam" section
3. Click **"Sync Steam Library"**

### Manual Library Entry
1. Select platform from dropdown
2. Enter game title
3. Optionally add App ID
4. Click **"Add"**

##  Project Structure

```
game_deals_assistant/
├── app/
│   ├── main.py              # FastAPI application & routes
│   ├── db.py                # SQLite database layer
│   ├── sources/
│   │   ├── steam.py         # Steam API integration
│   │   └── cheapshark.py    # CheapShark API integration
│   └── static/
│       ├── index.html       # Frontend UI
│       ├── styles.css       # Styling
│       └── script.js        # Frontend logic
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI/CD
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose setup
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

##  API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve main HTML |
| GET | `/api/me` | Get current user info |
| GET | `/api/stores` | List available stores |
| GET | `/api/deals` | Get filtered game deals |

### Query Parameters for /api/deals

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_discount` | int | 10 | Minimum discount % |
| `max_discount` | int | 100 | Maximum discount % |
| `store_id` | str | null | Filter by store |
| `source` | str | null | Filter by source (steam, cheapshark) |
| `title` | str | null | Search by game title |
| `max_price` | float | null | Maximum price filter |
| `free_only` | bool | false | Only free games |
| `hide_owned` | bool | false | Hide already owned |

### Favorites Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/favorites` | Create favorite |
| GET | `/api/favorites` | List favorites |
| DELETE | `/api/favorites/{id}` | Delete favorite |

### Library Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/owned-games` | List owned games |
| POST | `/api/owned-games/manual` | Add game manually |
| DELETE | `/api/owned-games/{id}` | Delete owned game |
| POST | `/api/steam/sync` | Sync Steam library |

##  Development

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Lint
flake8 app/
```

### Local Development with Hot Reload

```bash
python -m uvicorn app.main:app --reload --port 8000
```

##  Docker

### Build Image

```bash
docker build -t game-deals-assistant .
```

### Run Container

```bash
docker run -p 8000:8000 \
  -e STEAM_API_KEY=your_key_here \
  game-deals-assistant
```

### Docker Compose

```bash
# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

##  Dependencies

- **fastapi** - Modern Python web framework
- **uvicorn** - ASGI server
- **requests** - HTTP library
- **pydantic** - Data validation
- **python-dotenv** - Environment variables

See [requirements.txt](requirements.txt) for full list.

##  Deployment

### Render.com

1. Push to GitHub
2. Connect repository to Render
3. Add STEAM_API_KEY environment variable
4. Deploy

### Docker

```bash
docker-compose up -d
```

##  Troubleshooting

### Steam Library Sync Not Working
- Verify STEAM_API_KEY is set correctly
- Check SteamID64 is valid (17 digits)
- Ensure Steam profile is public
- Check internet connection

### Database Locked
- Restart the application
- Database will be automatically recovered

### Deals Not Loading
- Check internet connection
- Try adjusting discount range (0-100%)
- Try different sources
- Check if APIs are responding

##  Roadmap

- [ ] Email/Telegram notifications
- [ ] Epic Games integration
- [ ] GOG store API
- [ ] CSV/JSON export
- [ ] Price history tracking
- [ ] Multi-user accounts
- [ ] Advanced analytics
- [ ] Mobile app

##  License

MIT License - see LICENSE file for details

##  Contributing

Contributions welcome! Submit a Pull Request.

##  Support

- **Issues**: Create on GitHub
- **Email**: nodirmuhammedov_acer@outlook.com

##  Acknowledgments

- **Steam** - Store API access
- **CheapShark** - Deal aggregation service
- **FastAPI** - Modern web framework

---

**Made with ❤️ by Eqziz**
