# Game Deals Assistant

**Game Deals Assistant** is a personal web app for tracking game discounts, saving favorite deals, and marking games you already own.

The project is built with **FastAPI**, **SQLite**, and a simple **HTML/CSS/JavaScript** frontend.

## Features

- View real Steam discounts through Steam Store data.
- View general PC game deals through CheapShark.
- Filter games by discount percentage.
- Filter deals under a target price.
- Search games by title.
- Sort deals by discount, price, title, or store.
- Add deals to favorites.
- Add owned games manually.
- Mark games as **Already Owned**.
- Hide already owned games from the deals list.
- Basic Steam Library Sync structure through SteamID64 and Steam Web API key.
- “Support the Author” section instead of premium/paywall logic.

## Screenshots

Add your screenshots here later:

```text
docs/screenshots/home.png
docs/screenshots/deals.png
docs/screenshots/library.png
```

Example markdown:

```md
![Home screen](docs/screenshots/home.png)
```

## Tech Stack

- Python
- FastAPI
- Uvicorn
- SQLite
- Requests
- HTML
- CSS
- JavaScript

## Project Structure

```text
game_deals_assistant/
  app/
    main.py
    db.py
    sources/
      __init__.py
      steam.py
      cheapshark.py
    static/
      index.html
      styles.css
      script.js
  requirements.txt
  .env.example
  .gitignore
  README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/game-deals-assistant.git
cd game-deals-assistant
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the app:

```bash
python -m uvicorn app.main:app --reload
```

Open in your browser:

```text
http://127.0.0.1:8000
```

## Steam Library Sync

Steam Library Sync is prepared, but it requires a Steam Web API key.

Create a Steam Web API key and set it as an environment variable.

Windows PowerShell:

```powershell
$env:STEAM_API_KEY="YOUR_STEAM_API_KEY"
```

macOS/Linux:

```bash
export STEAM_API_KEY="YOUR_STEAM_API_KEY"
```

Then run the server:

```bash
python -m uvicorn app.main:app --reload
```

In the app, enter your **SteamID64** and click **Sync Steam Library**.

If you do not set a Steam API key, you can still manually add owned games.

## Support the Author

The app has a **Support the Author** button instead of premium/paywall logic.

To change the support details, open:

```text
app/static/index.html
```

Find this block:

```html
<div class="support-details">
```

Replace the placeholder data with your own:

```text
0000 0000 0000 0000
Your name
@your_username
```

You can also contact the author by email: nodirmuhammedov_acer@outlook.com

## Data Storage

The app uses SQLite.

After the first run, the database file will be created automatically:

```text
game_deals.db
```

This file is ignored by Git through `.gitignore`.

## Notes About Epic Games

Epic Games library sync is not implemented yet.

For now, Epic-owned games can be added manually. This is intentional because Epic does not provide a simple public library API like Steam's owned games endpoint.

## Roadmap

Possible next steps:

- Add real Epic Games deal source.
- Add CSV import for owned games.
- Add Telegram notifications.
- Add price history.
- Add user accounts.
- Add Docker support.
- Deploy the app online.

## Live Demo

https://your-render-link.onrender.com

## License

This project is currently for personal and educational use.
