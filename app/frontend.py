from hashlib import sha256
from pathlib import Path

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


class FrontendFiles(StaticFiles):
    """Serve HTML with asset URLs that change when the CSS or JavaScript changes."""

    def __init__(self, directory: Path):
        super().__init__(directory=directory)
        versions = {}
        for name in ("styles.css", "script.js"):
            url = f"/static/{name}"
            version = sha256((directory / name).read_bytes()).hexdigest()[:16]
            versions[url] = f"{url}?v={version}"

        self.pages = {}
        for path in directory.glob("*.html"):
            html = path.read_text(encoding="utf-8")
            for url, versioned_url in versions.items():
                html = html.replace(f'"{url}"', f'"{versioned_url}"')
            self.pages[path.name] = html

    def page(self, name):
        return HTMLResponse(self.pages[name], headers={"Cache-Control": "no-cache"})

    async def get_response(self, path, scope):
        if path in self.pages and scope["method"] in ("GET", "HEAD"):
            return self.page(path)
        return await super().get_response(path, scope)
