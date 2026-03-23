"""
QuickCart — Orders Section Tests
Endpoints:
  GET  /api/v1/orders
  GET  /api/v1/orders/{order_id}
  POST /api/v1/orders/{order_id}/cancel
  GET  /api/v1/orders/{order_id}/invoice

Run:
    pip install pytest requests
    pytest test_orders.py -v
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
def placed_order(valid_headers):
    """
    Place a fresh COD order with the cheapest product.
    Returns the full order object.
    """
    # Get cheapest active product
    products = requests.get(f"{BASE_URL}/admin/products",
                            headers={"X-Roll-Number": ROLL}).json()
    active = [p for p in products if p.get("is_active")]
    assert active, "No active product to create order"
    product = sorted(active, key=lambda p: p["price"])[0]

    # Clear cart and add product
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                  json={"product_id": product["product_id"], "quantity": 1})

    # Checkout with CARD so payment is already PAID
    res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                        json={"payment_method": "CARD"})
    assert res.status_code == 200, f"Could not place test order: {res.text}"
    data = res.json()
    return data.get("order") or data


# ═════════════════════════════════════════════════════════════════
# 1. GET /api/v1/orders
# ═════════════════════════════════════════════════════════════════

class TestGetOrders:

    def test_valid_request_returns_200(self, valid_headers):
        res = requests.get(f"{BASE_URL}/orders", headers=valid_headers)
        assert res.status_code == 200

    def test_response_is_list(self, valid_headers):
        res = requests.get(f"{BASE_URL}/orders", headers=valid_headers)
        assert isinstance(res.json(), list)

    def test_orders_have_required_fields(self, valid_headers, placed_order):
        res = requests.get(f"{BASE_URL}/orders", headers=valid_headers)
        orders = res.json()
        assert len(orders) > 0
        order = orders[0]
        for field in ("order_id", "total_amount", "payment_status", "order_status"):
            assert field in order, f"Missing field '{field}' in order listing"

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/orders", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/orders", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/orders", ROLL, "99999")


# ═════════════════════════════════════════════════════════════════
# 2. GET /api/v1/orders/{order_id}
# ═════════════════════════════════════════════════════════════════

class TestGetOrderById:

    def test_valid_order_returns_200(self, valid_headers, placed_order):
        res = requests.get(f"{BASE_URL}/orders/{placed_order['order_id']}",
                           headers=valid_headers)
        assert res.status_code == 200

    def test_correct_order_id_in_response(self, valid_headers, placed_order):
        res = requests.get(f"{BASE_URL}/orders/{placed_order['order_id']}",
                           headers=valid_headers)
        assert res.json().get("order_id") == placed_order["order_id"]

    def test_nonexistent_order_returns_404(self, valid_headers):
        res = requests.get(f"{BASE_URL}/orders/999999", headers=valid_headers)
        assert res.status_code == 404

    def test_missing_roll_number_returns_401(self, placed_order):
        assert_missing_roll_number_returns_401(
            f"{BASE_URL}/orders/{placed_order['order_id']}", USER_ID)

    def test_missing_user_id_returns_400(self, placed_order):
        assert_missing_user_id_returns_400(
            f"{BASE_URL}/orders/{placed_order['order_id']}", ROLL)


# ═════════════════════════════════════════════════════════════════
# 3. POST /api/v1/orders/{order_id}/cancel
# ═════════════════════════════════════════════════════════════════

class TestCancelOrder:

    @pytest.fixture
    def cancellable_order(self, valid_headers):
        """Place a fresh PENDING order that can be cancelled."""
        products = requests.get(f"{BASE_URL}/admin/products",
                                headers={"X-Roll-Number": ROLL}).json()
        active = sorted([p for p in products if p.get("is_active")], key=lambda p: p["price"])
        assert active
        requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": active[0]["product_id"], "quantity": 1})
        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "COD"})
        assert res.status_code == 200
        data = res.json()
        return (data.get("order") or data)["order_id"]

    def test_cancel_pending_order_returns_200(self, valid_headers, cancellable_order):
        res = requests.post(f"{BASE_URL}/orders/{cancellable_order}/cancel",
                            headers=valid_headers)
        assert res.status_code == 200

    def test_cancel_nonexistent_order_returns_404(self, valid_headers):
        res = requests.post(f"{BASE_URL}/orders/999999/cancel", headers=valid_headers)
        assert res.status_code == 404

    def test_cancel_delivered_order_returns_400(self, valid_headers):
        """Delivered orders cannot be cancelled."""
        all_orders = requests.get(f"{BASE_URL}/admin/orders",
                                  headers={"X-Roll-Number": ROLL}).json()
        delivered = [o for o in all_orders
                     if o.get("order_status") == "DELIVERED"
                     and str(o.get("user_id")) == USER_ID]
        if not delivered:
            pytest.skip("No delivered order available for this user")
        res = requests.post(f"{BASE_URL}/orders/{delivered[0]['order_id']}/cancel",
                            headers=valid_headers)
        assert res.status_code == 400

    def test_stock_restored_after_cancel(self, valid_headers):
        """Cancelling an order must add items back to product stock."""
        products = requests.get(f"{BASE_URL}/admin/products",
                                headers={"X-Roll-Number": ROLL}).json()
        active = sorted([p for p in products if p.get("is_active")], key=lambda p: p["price"])
        product = active[0]
        stock_before = product["stock"]

        requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
        requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                      json={"product_id": product["product_id"], "quantity": 1})
        res = requests.post(f"{BASE_URL}/checkout", headers=valid_headers,
                            json={"payment_method": "COD"})
        order_id = (res.json().get("order") or res.json())["order_id"]

        requests.post(f"{BASE_URL}/orders/{order_id}/cancel", headers=valid_headers)

        updated_products = requests.get(f"{BASE_URL}/admin/products",
                                        headers={"X-Roll-Number": ROLL}).json()
        updated = next(p for p in updated_products if p["product_id"] == product["product_id"])
        assert updated["stock"] == stock_before, (
            f"Stock not restored: before={stock_before}, after={updated['stock']}"
        )

    def test_missing_roll_number_returns_401(self, placed_order):
        assert_missing_roll_number_returns_401(
            f"{BASE_URL}/orders/{placed_order['order_id']}/cancel", USER_ID)

    def test_missing_user_id_returns_400(self, placed_order):
        assert_missing_user_id_returns_400(
            f"{BASE_URL}/orders/{placed_order['order_id']}/cancel", ROLL)


# ═════════════════════════════════════════════════════════════════
# 4. GET /api/v1/orders/{order_id}/invoice
# ═════════════════════════════════════════════════════════════════

class TestOrderInvoice:

    def test_invoice_returns_200(self, valid_headers, placed_order):
        res = requests.get(f"{BASE_URL}/orders/{placed_order['order_id']}/invoice",
                           headers=valid_headers)
        assert res.status_code == 200

    def test_invoice_has_subtotal_gst_total(self, valid_headers, placed_order):
        res = requests.get(f"{BASE_URL}/orders/{placed_order['order_id']}/invoice",
                           headers=valid_headers)
        data = res.json()
        for field in ("subtotal", "gst_amount", "total"):
            assert field in data, f"Invoice missing field '{field}'"

    def test_invoice_total_matches_order_total(self, valid_headers, placed_order):
        res = requests.get(f"{BASE_URL}/orders/{placed_order['order_id']}/invoice",
                           headers=valid_headers)
        invoice = res.json()
        assert abs(invoice["total"] - placed_order["total_amount"]) < 0.01, (
            f"Invoice total {invoice['total']} does not match order total {placed_order['total_amount']}"
        )

    def test_invoice_subtotal_plus_gst_equals_total(self, valid_headers, placed_order):
        res = requests.get(f"{BASE_URL}/orders/{placed_order['order_id']}/invoice",
                           headers=valid_headers)
        inv = res.json()
        assert abs((inv["subtotal"] + inv["gst_amount"]) - inv["total"]) < 0.01, (
            f"subtotal + gst != total: {inv['subtotal']} + {inv['gst_amount']} != {inv['total']}"
        )

    def test_nonexistent_order_invoice_returns_404(self, valid_headers):
        res = requests.get(f"{BASE_URL}/orders/999999/invoice", headers=valid_headers)
        assert res.status_code == 404

    def test_missing_roll_number_returns_401(self, placed_order):
        assert_missing_roll_number_returns_401(
            f"{BASE_URL}/orders/{placed_order['order_id']}/invoice", USER_ID)

    def test_missing_user_id_returns_400(self, placed_order):
        assert_missing_user_id_returns_400(
            f"{BASE_URL}/orders/{placed_order['order_id']}/invoice", ROLL)
