from uuid import uuid4
from pathlib import Path

import pytest


SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)


def take_shot(page, name: str) -> None:
    page.screenshot(path=str(SCREENSHOT_DIR / f"{name}.png"), full_page=True)


@pytest.mark.e2e
def test_register_success_ui(page, fastapi_server):
    unique = uuid4().hex[:8]
    email = f"user_{unique}@example.com"
    username = f"user_{unique}"
    password = "SecurePass123!"
    base_url = fastapi_server.rstrip("/")

    page.goto(f"{base_url}/register")

    page.fill("#first_name", "Alice")
    page.fill("#last_name", "Smith")
    page.fill("#email", email)
    page.fill("#username", username)
    page.fill("#password", password)
    page.fill("#confirm_password", password)

    take_shot(page, "register-form-filled")

    page.click("button[type=submit]")

    page.wait_for_timeout(1500)
    take_shot(page, "register-success")

    page_text = page.locator("body").inner_text().lower()
    assert (
        "success" in page_text
        or "registered" in page_text
        or "login" in page.url.lower()
    )


@pytest.mark.e2e
def test_register_short_password_ui(page, fastapi_server):
    unique = uuid4().hex[:8]
    email = f"short_{unique}@example.com"
    username = f"short_{unique}"
    base_url = fastapi_server.rstrip("/")
    page.goto(f"{base_url}/register")

    page.fill("#first_name", "Short")
    page.fill("#last_name", "Password")
    page.fill("#email", email)
    page.fill("#username", username)
    page.fill("#password", "123")
    page.fill("#confirm_password", "123")

    page.click("button[type=submit]")

    page.wait_for_timeout(1500)
    take_shot(page, "register-short-password-error")

    page_text = page.locator("body").inner_text().lower()
    assert (
        "password" in page_text
        or "error" in page_text
        or "invalid" in page_text
        or "least" in page_text
        or "minimum" in page_text
    )


@pytest.mark.e2e
def test_login_success_ui(page, fastapi_server):
    unique = uuid4().hex[:8]
    email = f"login_{unique}@example.com"
    username = f"login_{unique}"
    password = "SecurePass123!"
    base_url = fastapi_server.rstrip("/")
    page.goto(f"{base_url}/register")
    page.fill("#first_name", "Bob")
    page.fill("#last_name", "Jones")
    page.fill("#email", email)
    page.fill("#username", username)
    page.fill("#password", password)
    page.fill("#confirm_password", password)
    page.click("button[type=submit]")
    page.wait_for_timeout(1500)

    page.goto(f"{base_url}/login")
    page.fill("#username", username)
    page.fill("#password", password)

    take_shot(page, "login-form-filled")

    page.click("button[type=submit]")

    page.wait_for_timeout(2000)
    take_shot(page, "login-success")

    access_token = page.evaluate("localStorage.getItem('access_token')")
    assert access_token is not None
    assert len(access_token) > 0


@pytest.mark.e2e
def test_login_invalid_credentials_ui(page, fastapi_server):
    base_url = fastapi_server.rstrip("/")
    page.goto(f"{base_url}/login")

    page.fill("#username", "wronguser")
    page.fill("#password", "wrongpassword")

    page.click("button[type=submit]")

    page.wait_for_timeout(1500)
    take_shot(page, "login-invalid-credentials")

    page_text = page.locator("body").inner_text().lower()
    assert (
        "invalid" in page_text
        or "incorrect" in page_text
        or "error" in page_text
        or "unauthorized" in page_text
    )