import pytest

from app.sources import steam


@pytest.mark.parametrize(("page", "size", "expected_ids", "next_page"), [
    (1, 3, range(3, 6), 2),
    (1, 30, range(30, 60), 2),
    (1, 60, range(60, 65), None),
    (10, 10, range(0), None),
])
def test_steam_slices_source_pages(monkeypatch, page, size, expected_ids, next_page):
    class SearchResult:
        def __init__(self, start):
            self.start = start

        def raise_for_status(self):
            pass

        def json(self):
            rows = "".join(
                f'<a class="search_result_row" data-ds-appid="{i}">'
                f'<span class="title">Game {i}</span><span class="discount_pct">-50%</span>'
                '<span class="discount_original_price">$2.00</span>'
                '<span class="discount_final_price">$1.00</span></a>'
                for i in range(self.start, min(self.start + 50, 65))
            )
            return {"success": 1, "total_count": 65, "start": self.start, "results_html": rows}

    def fetch(url, *, params, **kwargs):
        assert params["count"] == 50 and params["infinite"] == 1
        return SearchResult((params["page"] - 1) * params["count"])

    monkeypatch.setattr(steam.requests, "get", fetch)
    data = steam.fetch_steam_deals(page=page, page_size=size)
    assert [int(deal["steam_app_id"]) for deal in data["deals"]] == list(expected_ids)
    assert data["next_page"] == next_page
