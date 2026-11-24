import pytest
from playwright.sync_api import Page, expect

from pages.account_page import AccountPage
from pages.home_page import HomePage
from pages.login_page import LoginPage

pytestmark = [pytest.mark.ui]


def test_search_unknown_keyword_shows_no_results_message(page: Page):
    """Goal: empty search state.
    Precondition: none.
    Expected: the message 'There are no products found.' and zero product cards."""
    home = HomePage(page).open().search("zzz-no-such-tool")
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)


@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_sort_by_price_orders_products(page: Page, order: str):
    """Goal: sorting by price in ascending or descending order.
    Precondition: none.
    Expected: prices on the first page are sorted in the chosen direction."""
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    home.sort_by(order)
    expect(home.sorting_completed).to_be_visible()
    prices = home.prices()
    assert prices == sorted(prices, reverse=order.endswith("desc")), prices


def test_filter_by_category_hammer_shows_matching_products(page: Page):
    """Goal: filtering products by Hammer category.
    Precondition: check the 'Hammer' category checkbox in filters sidebar.
    Expected: every product card listed on the page contains 'Hammer' in its name."""
    home = HomePage(page).open()
    home.filter_by_category("Hammer")
    expect(home.product_names.first).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names, "No products found for Hammer category"
    assert all("hammer" in n.lower() for n in names), names


def test_product_detail_shows_matching_name_and_price(page: Page):
    """Goal: product detail page displays matching product name and price from homepage card.
    Precondition: click the first product card from homepage.
    Expected: product detail name and unit price match the clicked product card."""
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    first_name = home.product_names.first.inner_text().strip()
    first_price = home.prices()[0]

    product = home.open_product(first_name)
    expect(product.name).to_have_text(first_name)
    assert product.price() == pytest.approx(first_price)


def test_cart_line_price_equals_unit_price_times_quantity(page: Page):
    """Goal: cart arithmetic verification for item line price and cart total.
    Precondition: empty cart and add Combination Pliers with quantity 2.
    Expected: line price = unit price x 2 and total = sum of line prices."""
    product = HomePage(page).open().open_product("Combination Pliers")
    unit = product.price()
    product.add_to_cart(quantity=2)
    expect(product.cart_quantity).to_have_text("2")
    cart = product.go_to_cart()
    expect(cart.product_titles).to_have_count(1)
    assert cart.line_totals() == [pytest.approx(unit * 2)]
    assert cart.total_value() == pytest.approx(sum(cart.line_totals()))


def test_cart_continue_shopping_returns_to_home(page: Page):
    """Goal: continue shopping button navigates back to homepage.
    Precondition: add a product to cart and open the checkout/cart page.
    Expected: clicking 'Continue Shopping' navigates back to homepage with product grid visible."""
    cart = HomePage(page).open().open_product("Hammer").add_to_cart().go_to_cart()
    expect(cart.product_titles.first).to_have_text("Hammer")
    cart.continue_shopping.click()
    expect(HomePage(page).product_names.first).to_be_visible()


def test_login_empty_form_shows_required_errors(page: Page):
    """Goal: client-side validation on empty login form submission.
    Precondition: none.
    Expected: 'Email is required' and 'Password is required' error messages displayed."""
    login = LoginPage(page).open()
    login.submit_button.click()
    expect(login.email_error).to_contain_text("Email is required")
    expect(login.password_error).to_contain_text("Password is required")


def test_account_page_logged_in_shows_user_profile(logged_in_page: Page):
    """Goal: reuse saved authentication state from auth_state fixture.
    Precondition: logged_in_page fixture with pre-authenticated storage state.
    Expected: AccountPage opens with title 'My account' and user menu contains 'QA Bot'."""
    account = AccountPage(logged_in_page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")
