import json
import re

import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage

pytestmark = [pytest.mark.ui]

PRODUCT_LIST = re.compile(r"/products(\?.*)?$")
EMPTY_PAGE = {
    "current_page": 1,
    "data": [],
    "from": None,
    "last_page": 1,
    "per_page": 9,
    "to": None,
    "total": 0,
}


def test_network_block_images_page_still_lists_products(page: Page):
    """Goal: the page works properly without downloading images.
    Precondition: route aborts all image requests (.png, .jpg, .jpeg, .webp, .avif, .svg).
    Expected: product names are visible and at least one image request was blocked."""
    blocked = []

    def block(route):
        blocked.append(route.request.url)
        route.abort()

    page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), block)
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    assert blocked, "no image request was blocked"


def test_network_empty_product_list_shows_no_results(page: Page):
    """Goal: empty state of the product grid.
    Precondition: list API mocked with EMPTY_PAGE response.
    Expected: 'There are no products found.' message is shown and 0 product cards displayed."""
    page.route(
        PRODUCT_LIST,
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(EMPTY_PAGE),
        ),
    )
    home = HomePage(page).open()
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)
