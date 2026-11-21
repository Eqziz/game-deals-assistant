"""Run against a local app with python tests/browser_smoke.py [URL]."""
import asyncio
import os
import sys
from urllib.parse import parse_qs, urlsplit

from playwright.async_api import async_playwright, expect


async def check(browser, base_url, width, language):
    page = await browser.new_page(viewport={"width": width, "height": 900})
    await page.add_init_script(f"localStorage.setItem('language', '{language}')")
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    requests = []
    favorites = []
    title = "The Long Expedition " + "X" * 72
    stale_started = asyncio.Event()
    stale_finished = asyncio.Event()

    async def api(route):
        req = route.request
        parts = urlsplit(req.url)
        status = 200
        if parts.path == "/api/me":
            data = {"authenticated": True, "user": {"name": "Player", "email": "player@example.org"}}
        elif parts.path == "/api/stores":
            data = {"all": [{"store_id": "1", "store_name": "Steam"}]}
        elif parts.path == "/api/deals":
            query = {k: vals[0] for k, vals in parse_qs(parts.query).items()}
            requests.append(query)
            search = query.get("title")
            if search == "slow":
                stale_started.set()
                await stale_finished.wait()
            if search == "retry" and sum(r.get("title") == "retry" for r in requests) == 1:
                status, data = 503, {"detail": "Unavailable"}
            else:
                number = int(query.get("page", 0))
                deal = {"title": search or title, "deal_url": f"https://example.org/game/{number}",
                        "normal_price": 24.99, "sale_price": 4.99, "savings": 80,
                        "thumb": base_url + "/missing-image", "store_name": "Steam", "is_favorite": False}
                data = {"deals": [deal], "next_page": 1 if number == 0 else None}
        elif parts.path == "/api/favorites":
            if req.method == "POST":
                favorites.append({**req.post_data_json, "id": 1})
                data = {"status": "saved"}
            else:
                data = favorites
        else:
            data = []
        await route.fulfill(status=status, json=data)

    await page.route("**/api/**", api)
    await page.goto(base_url)
    heading = page.locator("#dealRows h3").first
    await expect(heading).to_have_text(title)
    assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    await expect(page.locator("html")).to_have_attribute("lang", language)
    await expect(page.locator("#advanced")).to_be_hidden()
    opener = page.locator("#dealRows [data-action=target]").first
    await opener.click()
    await expect(page.locator("#targetPrice")).to_be_focused()
    await page.keyboard.press("Escape")
    await expect(opener).to_be_focused()
    await opener.click()
    await page.locator("#targetPrice").fill("4.99")
    await page.locator("#priceForm .primary").click()
    await expect(page.locator("#priceDialog")).to_be_hidden()
    assert favorites[0]["target_price"] == 4.99
    await page.locator("[data-preset=under5]").click()
    await page.locator("#store").select_option("1")
    await page.locator("#query").fill("slow")
    await asyncio.wait_for(stale_started.wait(), 5)
    await page.locator("#query").fill("latest")
    await expect(heading).to_have_text("latest")
    stale_finished.set()
    await page.locator("#more").click()
    await expect(page.locator("#dealRows article")).to_have_count(2)
    assert requests[-1].items() >= {"page": "1", "title": "latest", "store_id": "1", "max_price": "5"}.items()
    await expect(heading).to_have_text("latest")
    await page.locator("#query").fill("retry")
    retry = page.locator("#dealStatus button")
    await retry.click()
    await expect(heading).to_have_text("retry")
    assert requests[-1] == requests[-2]
    await page.locator('nav a[href="#favorites"]').click()
    await expect(page.locator("#favoriteRows h3")).to_have_text(title)
    assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    assert not errors, errors
    await page.close()


async def main():
    base_url = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(channel=os.getenv("BROWSER_CHANNEL", "chrome"))
        try:
            for width in (320, 768, 1280):
                for language in ("ru", "en"):
                    await check(browser, base_url, width, language)
                    print(f"OK {width}px {language}", flush=True)
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
