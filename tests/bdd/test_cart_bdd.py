import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.cart_page import CartPage
from pages.home_page import HomePage
from pages.product_page import ProductPage

pytestmark = [pytest.mark.bdd, pytest.mark.ui]

scenarios("cart.feature")


@given("I am on the home page", target_fixture="home")
def home(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    return home


@when(parsers.parse('I search for "{product}"'))
def search_product(home: HomePage, product: str):
    home.search(product)


@when(parsers.parse('I open the product "{product}"'), target_fixture="product_page")
def open_product(home: HomePage, product: str) -> ProductPage:
    return home.open_product(product)


@when(parsers.parse("I add it to the cart with quantity {quantity:d}"), target_fixture="unit_price")
def add_to_cart(product_page: ProductPage, quantity: int) -> float:
    unit_price = product_page.price()
    product_page.add_to_cart(quantity=quantity)
    expect(product_page.cart_quantity).to_have_text(str(quantity))
    return unit_price


@when("I go to the cart", target_fixture="cart_page")
def go_to_cart(product_page: ProductPage) -> CartPage:
    return product_page.go_to_cart()


@then(parsers.parse('the cart item "{product}" has line price matching unit price times quantity {quantity:d}'))
def verify_line_price(cart_page: CartPage, product: str, quantity: int, unit_price: float):
    expect(cart_page.product_titles.first).to_have_text(product)
    expected_line_price = unit_price * quantity
    assert cart_page.line_totals() == [pytest.approx(expected_line_price)]


@then("the cart total equals the line price")
def verify_cart_total(cart_page: CartPage):
    assert cart_page.total_value() == pytest.approx(sum(cart_page.line_totals()))
