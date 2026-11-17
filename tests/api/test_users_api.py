import pytest
from playwright.sync_api import APIRequestContext

pytestmark = [pytest.mark.api]


def test_users_register_empty_body_returns_422_with_field_errors(api: APIRequestContext):
    """Goal: server-side validation on registration.
    Precondition: send empty payload to /users/register.
    Expected: 422 Unprocessable Entity and error lists for 'email' and 'password'."""
    response = api.post("/users/register", data={})
    assert response.status == 422, response.text()
    errors = response.json()
    assert "email" in errors and "password" in errors, errors


def test_users_me_with_token_returns_own_profile(api: APIRequestContext, auth_headers: dict, test_user: dict):
    """Goal: bearer token grants access to personal profile.
    Precondition: user registered and provided valid authorization token header.
    Expected: 200 OK and response body email matches the registered user email."""
    response = api.get("/users/me", headers=auth_headers)
    assert response.status == 200, response.text()
    assert response.json()["email"] == test_user["email"]
