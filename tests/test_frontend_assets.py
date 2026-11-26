from hashlib import sha256

import pytest
from bs4 import BeautifulSoup
from fastapi.testclient import TestClient

from app.main import app


@pytest.mark.parametrize("path", ["/", "/static/index.html", "/static/privacy.html", "/static/terms.html"])
def test_html_revalidates_and_references_current_assets(path):
    client = TestClient(app)
    page = client.get(path)
    assert page.status_code == 200
    assert page.headers["cache-control"] == "no-cache"
    html = BeautifulSoup(page.content, "html.parser")
    urls = [html.select_one('link[rel="stylesheet"]')["href"]]
    if path in ("/", "/static/index.html"):
        urls.append(html.select_one("script[src]")["src"])
    for url in urls:
        asset = client.get(url)
        assert asset.status_code == 200
        assert url.endswith("?v=" + sha256(asset.content).hexdigest()[:16])
