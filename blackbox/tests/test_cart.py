"""
QuickCart — Cart Section Tests
Endpoints:
  GET    /api/v1/cart
  POST   /api/v1/cart/add
  POST   /api/v1/cart/update
  POST   /api/v1/cart/remove
  DELETE /api/v1/cart/clear

Run:
    pip install pytest requests
    pytest test_cart.py -v
"""

import pytest
import requests
from header_validation import (
    assert_missing_roll_number_returns_401,
    assert_invalid_roll_number_returns_400,
    assert_missing_user_id_returns_400,
    assert_nonexistent_user_id_returns_400,
    assert_invalid_user_id_returns_400,
)

BASE_URL = "http://localhost:8080/api/v1"
ROLL     = "2024111004"   # ← replace with your roll number
USER_ID  = "1"            # ← replace with a valid user ID


# ── fixtures ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def valid_headers():
    return {
        "X-Roll-Number": ROLL,
        "X-User-ID":     USER_ID,
    }

@pytest.fixture(scope="session")
def active_product_id(valid_headers):
    """Fetch a valid active product ID from admin endpoint."""
    res = requests.get(f"{BASE_URL}/admin/products",
                       headers={"X-Roll-Number": ROLL})
    assert res.status_code == 200
    products = res.json()
    active = [p for p in products if p.get("is_active")]
    assert active, "No active products found — seed the server first"
    return active[0]["product_id"]

@pytest.fixture(autouse=True)
def clear_cart(valid_headers):
    """Clear the cart before every test to ensure a clean state."""
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    yield
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)


# ═════════════════════════════════════════════════════════════════
# 1. GET /api/v1/cart
# ═════════════════════════════════════════════════════════════════

class TestGetCart:

    def test_empty_cart_returns_200(self, valid_headers):
        res = requests.get(f"{BASE_URL}/cart", headers=valid_headers)
        assert res.status_code == 200

    def test_empty_cart_has_zero_total(self, valid_headers):
        res = requests.get(f"{BASE_URL}/cart", headers=valid_headers)
        data = res.json()
        assert "total" in data
        assert data["total"] == 0 or data["total"] == 0.0

    def test_cart_has_items_field(self, valid_headers):
        res = requests.get(f"{BASE_URL}/cart", headers=valid_headers)
        assert "items" in res.json()

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/cart", USER_ID)

    def test_invalid_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/cart", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/cart", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/cart", ROLL, "99999")


# ═════════════════════════════════════════════════════════════════
# 2. POST /api/v1/cart/add
# ═════════════════════════════════════════════════════════════════

class TestCartAdd:

    def test_add_valid_product_returns_200(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                            json={"product_id": active_product_id, "quantity": 1})
        assert res.status_code == 200

    def test_add_zero_quantity_returns_400(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                            json={"product_id": active_product_id, "quantity": 0})
        assert res.status_code == 400

    def test_add_negative_quantity_returns_400(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                            json={"product_id": active_product_id, "quantity": -1})
        assert res.status_code == 400

    def test_add_nonexistent_product_returns_404(self, valid_headers):
        res = requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                            json={"product_id": 999999, "quantity": 1})
        assert res.status_code == 404

    def test_add_duplicate_product_accumulates_quantity(self, valid_headers, active_product_id):
        """Adding the same product twice must sum quantities, not replace."""
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 1})
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 2})
        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        item = next((i for i in cart["items"] if i["product_id"] == active_product_id), None)
        assert item is not None
        assert item["quantity"] == 3, f"Expected qty 3 (accumulated), got {item['quantity']}"

    def test_cart_subtotal_correct_after_add(self, valid_headers, active_product_id):
        """Each item's subtotal must equal quantity × unit_price."""
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 2})
        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        item = next((i for i in cart["items"] if i["product_id"] == active_product_id), None)
        assert item is not None
        expected_subtotal = round(item["quantity"] * item["unit_price"], 2)
        assert abs(item["subtotal"] - expected_subtotal) < 0.01, (
            f"Subtotal mismatch: got {item['subtotal']}, expected {expected_subtotal}"
        )

    def test_cart_total_is_sum_of_subtotals(self, valid_headers, active_product_id):
        """Cart total must equal the sum of all item subtotals."""
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 3})
        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        expected_total = round(sum(i["subtotal"] for i in cart["items"]), 2)
        assert abs(round(cart["total"], 2) - expected_total) < 0.01, (
            f"Cart total mismatch: got {cart['total']}, expected {expected_total}"
        )

    def test_add_over_stock_quantity_returns_400(self, valid_headers, active_product_id):
        """Requesting more than in-stock quantity must be rejected."""
        res = requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                            json={"product_id": active_product_id, "quantity": 999999})
        assert res.status_code == 400

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/cart/add", USER_ID)

    def test_invalid_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/cart/add", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/cart/add", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/cart/add", ROLL, "99999")


# ═════════════════════════════════════════════════════════════════
# 3. POST /api/v1/cart/update
# ═════════════════════════════════════════════════════════════════

class TestCartUpdate:

    def test_update_quantity_to_valid_value(self, valid_headers, active_product_id):
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 1})
        res = requests.post(f"{BASE_URL}/cart/update", headers=valid_headers,
                            json={"product_id": active_product_id, "quantity": 3})
        assert res.status_code == 200

    def test_update_quantity_to_zero_returns_400(self, valid_headers, active_product_id):
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 1})
        res = requests.post(f"{BASE_URL}/cart/update", headers=valid_headers,
                            json={"product_id": active_product_id, "quantity": 0})
        assert res.status_code == 400

    def test_update_quantity_negative_returns_400(self, valid_headers, active_product_id):
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 1})
        res = requests.post(f"{BASE_URL}/cart/update", headers=valid_headers,
                            json={"product_id": active_product_id, "quantity": -5})
        assert res.status_code == 400

    def test_update_reflects_new_quantity(self, valid_headers, active_product_id):
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 1})
        requests.post(f"{BASE_URL}/cart/update", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 5})
        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        item = next((i for i in cart["items"] if i["product_id"] == active_product_id), None)
        assert item["quantity"] == 5, f"Expected updated qty 5, got {item['quantity']}"

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/cart/update", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/cart/update", ROLL)


# ═════════════════════════════════════════════════════════════════
# 4. POST /api/v1/cart/remove
# ═════════════════════════════════════════════════════════════════

class TestCartRemove:

    def test_remove_existing_item_returns_200(self, valid_headers, active_product_id):
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 1})
        res = requests.post(f"{BASE_URL}/cart/remove", headers=valid_headers,
                            json={"product_id": active_product_id})
        assert res.status_code == 200

    def test_remove_item_not_in_cart_returns_404(self, valid_headers):
        res = requests.post(f"{BASE_URL}/cart/remove", headers=valid_headers,
                            json={"product_id": 999999})
        assert res.status_code == 404

    def test_remove_reduces_item_count(self, valid_headers, active_product_id):
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 1})
        requests.post(f"{BASE_URL}/cart/remove", headers=valid_headers,
                      json={"product_id": active_product_id})
        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        ids = [i["product_id"] for i in cart["items"]]
        assert active_product_id not in ids

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/cart/remove", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/cart/remove", ROLL)


# ═════════════════════════════════════════════════════════════════
# 5. DELETE /api/v1/cart/clear
# ═════════════════════════════════════════════════════════════════

class TestCartClear:

    def test_clear_non_empty_cart_returns_200(self, valid_headers, active_product_id):
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 1})
        res = requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
        assert res.status_code == 200

    def test_clear_empty_cart_returns_200(self, valid_headers):
        res = requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
        assert res.status_code == 200

    def test_cart_is_empty_after_clear(self, valid_headers, active_product_id):
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active_product_id, "quantity": 2})
        requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        assert cart["items"] == []
        assert cart["total"] == 0 or cart["total"] == 0.0

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/cart/clear", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/cart/clear", ROLL)
