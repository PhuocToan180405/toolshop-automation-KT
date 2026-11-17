import pytest
from playwright.sync_api import APIRequestContext

pytestmark = [pytest.mark.api]


@pytest.fixture
def new_cart(api: APIRequestContext) -> str:
    response = api.post("/carts")
    assert response.status == 201, response.text()
    return response.json()["id"]


def test_cart_add_product_quantity_two_is_stored(api: APIRequestContext, new_cart: str):
    """Goal: cart API stores the added product and its quantity.
    Precondition: a new cart fixture and the first product from GET /products.
    Expected: GET /carts/{id} has exactly 1 item, quantity 2, and matching product_id."""
    product = api.get("/products", params={"page": 1}).json()["data"][0]
    added = api.post(f"/carts/{new_cart}", data={"product_id": product["id"], "quantity": 2})
    assert added.ok, added.text()
    items = api.get(f"/carts/{new_cart}").json()["cart_items"]
    assert len(items) == 1
    assert items[0]["quantity"] == 2
    assert str(items[0]["product_id"]) == str(product["id"])
