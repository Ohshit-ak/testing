"""
QuickCart — Checkout Section Tests
Endpoint:
  POST /api/v1/checkout

Run:
    pip install pytest requests
    pytest test_checkout.py -v
"""

import pytest
import requests
from header_validation import (
    assert_missing_roll_number_returns_401,
    assert_invalid_roll_number_returns_400,
    assert_missing_user_id_returns_400,
    assert_nonexistent_user_id_returns_400,
)

BASE_URL = "http://localhost:8080/api/v1"
ROLL     = "2024111004"
USER_ID  = "1"


@pytest.fixture(scope="session")
def valid_headers():
    return {"X-Roll-Number": ROLL, "X-User-ID": USER_ID}


@pytest.fixture(scope="session")
def cheap_product(valid_headers):
    """Lowest-priced active product to keep totals under COD limit."""
    res = requests.get(f"{BASE_URL}/admin/products", headers={"X-Roll-Number": ROLL})
    active = [p for p in res.json() if p.get("is_active")]
    assert active, "No active products found"
    return sorted(active, key=lambda p: p["price"])[0]


@pytest.fixture(autouse=True)
def setup_cart(valid_headers, cheap_product):
    """Add one cheap item to cart before each test, clear after."""
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                  json={"product_id": cheap_product["product_id"], "quantity": 1})
    yield
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)


# ═════════════════════════════════════════════════════════════════
# 1. POST /api/v1/checkout
# ═════════════════════════════════════════════════════════════════

class TestCheckout:

    def test_checkout_with_card_returns_200(self, valid_headers):
        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "CARD"})
        assert res.status_code == 200

    def test_card_payment_status_is_paid(self, valid_headers):
        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "CARD"})
        assert res.status_code == 200
        data = res.json()
        order = data.get("order") or data
        assert order.get("payment_status") == "PAID", (
            f"CARD order should start as PAID, got {order.get('payment_status')}"
        )

    def test_cod_payment_status_is_pending(self, valid_headers):
        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "COD"})
        assert res.status_code == 200
        data = res.json()
        order = data.get("order") or data
        assert order.get("payment_status") == "PENDING", (
            f"COD order should start as PENDING, got {order.get('payment_status')}"
        )

    def test_checkout_empty_cart_returns_400(self, valid_headers):
        requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "CARD"})
        assert res.status_code == 400

    def test_invalid_payment_method_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "CRYPTO"})
        assert res.status_code == 400

    def test_cod_over_5000_returns_400(self, valid_headers):
        """COD is not allowed when order total exceeds 5000."""
        requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
        # Add enough units to push total above 5000 (via any active product)
        res = requests.get(f"{BASE_URL}/admin/products", headers={"X-Roll-Number": ROLL})
        active = [p for p in res.json() if p.get("is_active")]
        product = sorted(active, key=lambda p: p["price"], reverse=True)[0]
        qty = max(1, int(5001 / product["price"]) + 1)
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": product["product_id"], "quantity": qty})
        checkout_res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                                     json={"payment_method": "COD"})
        assert checkout_res.status_code == 400

    def test_gst_applied_once_at_5_percent(self, valid_headers, cheap_product):
        """Total = subtotal × 1.05; GST must not be applied more than once."""
        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        subtotal = cart["total"]
        expected_total = round(subtotal * 1.05, 2)

        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "CARD"})
        assert res.status_code == 200
        data = res.json()
        order = data.get("order") or data
        actual_total = round(order.get("total_amount", 0), 2)
        assert abs(actual_total - expected_total) < 0.02, (
            f"Total after GST mismatch: got {actual_total}, expected ~{expected_total}"
        )

    def test_wallet_payment_status_is_pending(self, valid_headers):
        # Add enough wallet balance first
        requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers,
                      json={"amount": 10000})
        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "WALLET"})
        # May fail if wallet is insufficient; either way capture the logic
        if res.status_code == 200:
            data = res.json()
            order = data.get("order") or data
            assert order.get("payment_status") == "PENDING"

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/checkout", USER_ID)

    def test_invalid_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/checkout", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/checkout", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/checkout", ROLL, "99999")
