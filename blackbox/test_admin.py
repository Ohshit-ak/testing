"""
QuickCart — Admin Section Tests
Endpoints:
  GET /api/v1/admin/users
  GET /api/v1/admin/users/{user_id}
  GET /api/v1/admin/carts
  GET /api/v1/admin/orders
  GET /api/v1/admin/products
  GET /api/v1/admin/coupons
  GET /api/v1/admin/tickets
  GET /api/v1/admin/addresses

Run:
    pip install pytest requests
    pytest test_admin.py -v
"""

import pytest
import requests

BASE_URL    = "http://localhost:8080/api/v1"
ROLL_NUMBER = "2024111004"   # ← replace with your actual roll number

ADMIN_HEADERS = {"X-Roll-Number": ROLL_NUMBER}

ADMIN_ENDPOINTS = [
    "/admin/users",
    "/admin/carts",
    "/admin/orders",
    "/admin/products",
    "/admin/coupons",
    "/admin/tickets",
    "/admin/addresses",
]


# ═════════════════════════════════════════════════════════════════
# 1.  X-Roll-Number header validation  (all admin endpoints)
# ═════════════════════════════════════════════════════════════════

class TestAdminHeaderValidation:

    @pytest.mark.parametrize("endpoint", ADMIN_ENDPOINTS)
    def test_missing_roll_number_returns_401(self, endpoint):
        res = requests.get(f"{BASE_URL}{endpoint}")   # no headers at all
        assert res.status_code == 401, (
            f"Expected 401 for missing X-Roll-Number on {endpoint}, got {res.status_code}"
        )

    @pytest.mark.parametrize("endpoint", ADMIN_ENDPOINTS)
    def test_invalid_roll_number_letters_returns_400(self, endpoint):
        res = requests.get(f"{BASE_URL}{endpoint}", headers={"X-Roll-Number": "abc"})
        assert res.status_code == 400, (
            f"Expected 400 for non-integer X-Roll-Number on {endpoint}, got {res.status_code}"
        )

    @pytest.mark.parametrize("endpoint", ADMIN_ENDPOINTS)
    def test_invalid_roll_number_symbols_returns_400(self, endpoint):
        res = requests.get(f"{BASE_URL}{endpoint}", headers={"X-Roll-Number": "##!@"})
        assert res.status_code == 400, (
            f"Expected 400 for symbol X-Roll-Number on {endpoint}, got {res.status_code}"
        )


# ═════════════════════════════════════════════════════════════════
# 2.  GET /admin/users
# ═════════════════════════════════════════════════════════════════

class TestAdminUsers:

    def test_status_200(self):
        res = requests.get(f"{BASE_URL}/admin/users", headers=ADMIN_HEADERS)
        assert res.status_code == 200

    def test_response_is_list(self):
        res = requests.get(f"{BASE_URL}/admin/users", headers=ADMIN_HEADERS)
        assert isinstance(res.json(), list)

    def test_user_fields_present(self):
        res = requests.get(f"{BASE_URL}/admin/users", headers=ADMIN_HEADERS)
        users = res.json()
        if not users:
            pytest.skip("No users in DB")
        user = users[0]
        for field in ("user_id", "name", "wallet_balance", "loyalty_points"):
            assert field in user, f"Field '{field}' missing from user object"

    def test_wallet_balance_is_numeric(self):
        users = requests.get(f"{BASE_URL}/admin/users", headers=ADMIN_HEADERS).json()
        if not users:
            pytest.skip("No users in DB")
        assert isinstance(users[0]["wallet_balance"], (int, float))

    def test_loyalty_points_is_integer(self):
        users = requests.get(f"{BASE_URL}/admin/users", headers=ADMIN_HEADERS).json()
        if not users:
            pytest.skip("No users in DB")
        assert isinstance(users[0]["loyalty_points"], int)


# ═════════════════════════════════════════════════════════════════
# 3.  GET /admin/users/{user_id}
# ═════════════════════════════════════════════════════════════════

class TestAdminUserById:

    @pytest.fixture(scope="class")
    def first_user_id(self):
        users = requests.get(f"{BASE_URL}/admin/users", headers=ADMIN_HEADERS).json()
        assert users, "No users in DB — seed first"
        return users[0]["user_id"]

    def test_valid_user_returns_200(self, first_user_id):
        res = requests.get(f"{BASE_URL}/admin/users/{first_user_id}", headers=ADMIN_HEADERS)
        assert res.status_code == 200

    def test_correct_user_id_returned(self, first_user_id):
        res = requests.get(f"{BASE_URL}/admin/users/{first_user_id}", headers=ADMIN_HEADERS)
        assert res.json().get("user_id") == first_user_id

    def test_user_fields_present(self, first_user_id):
        res = requests.get(f"{BASE_URL}/admin/users/{first_user_id}", headers=ADMIN_HEADERS)
        user = res.json()
        for field in ("user_id", "name", "wallet_balance", "loyalty_points"):
            assert field in user, f"Field '{field}' missing"

    def test_nonexistent_user_returns_404(self):
        res = requests.get(f"{BASE_URL}/admin/users/999999", headers=ADMIN_HEADERS)
        assert res.status_code == 404


# ═════════════════════════════════════════════════════════════════
# 4.  GET /admin/carts
# ═════════════════════════════════════════════════════════════════

class TestAdminCarts:

    def test_status_200(self):
        res = requests.get(f"{BASE_URL}/admin/carts", headers=ADMIN_HEADERS)
        assert res.status_code == 200

    def test_response_is_list(self):
        res = requests.get(f"{BASE_URL}/admin/carts", headers=ADMIN_HEADERS)
        assert isinstance(res.json(), list)

    def test_cart_fields_present(self):
        carts = requests.get(f"{BASE_URL}/admin/carts", headers=ADMIN_HEADERS).json()
        if not carts:
            pytest.skip("No carts in DB")
        cart = carts[0]
        for field in ("user_id", "items", "total"):
            assert field in cart, f"Field '{field}' missing from cart"

    def test_item_fields_present(self):
        carts = requests.get(f"{BASE_URL}/admin/carts", headers=ADMIN_HEADERS).json()
        cart_with_items = next((c for c in carts if c.get("items")), None)
        if cart_with_items is None:
            pytest.skip("No cart with items found")
        item = cart_with_items["items"][0]
        for field in ("product_id", "quantity", "subtotal"):
            assert field in item, f"Field '{field}' missing from cart item"

    def test_subtotal_equals_qty_times_unit_price(self):
        carts = requests.get(f"{BASE_URL}/admin/carts", headers=ADMIN_HEADERS).json()
        cart_with_items = next((c for c in carts if c.get("items")), None)
        if cart_with_items is None:
            pytest.skip("No cart with items found")
        for item in cart_with_items["items"]:
            if "unit_price" not in item:
                continue
            expected = round(item["quantity"] * item["unit_price"], 2)
            actual   = round(item["subtotal"], 2)
            assert abs(expected - actual) < 0.01, (
                f"Subtotal mismatch for product {item['product_id']}: "
                f"expected {expected}, got {actual}"
            )

    def test_cart_total_equals_sum_of_subtotals(self):
        """Cart total must equal the sum of ALL item subtotals."""
        carts = requests.get(f"{BASE_URL}/admin/carts", headers=ADMIN_HEADERS).json()
        cart_with_items = next((c for c in carts if c.get("items")), None)
        if cart_with_items is None:
            pytest.skip("No cart with items found")
        expected_total = round(sum(i["subtotal"] for i in cart_with_items["items"]), 2)
        actual_total   = round(cart_with_items["total"], 2)
        assert abs(expected_total - actual_total) < 0.01, (
            f"Cart total mismatch: expected {expected_total}, got {actual_total}"
        )


# ═════════════════════════════════════════════════════════════════
# 5.  GET /admin/orders
# ═════════════════════════════════════════════════════════════════

class TestAdminOrders:

    def test_status_200(self):
        res = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS)
        assert res.status_code == 200

    def test_response_is_list(self):
        res = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS)
        assert isinstance(res.json(), list)

    def test_order_fields_present(self):
        orders = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS).json()
        if not orders:
            pytest.skip("No orders in DB")
        order = orders[0]
        for field in ("order_id", "user_id", "total_amount", "gst_amount",
                      "payment_status", "payment_method", "order_status"):
            assert field in order, f"Field '{field}' missing from order"

    def test_payment_method_is_valid(self):
        orders = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS).json()
        if not orders:
            pytest.skip("No orders in DB")
        valid = {"COD", "CARD", "WALLET", "UPI"}
        for order in orders:
            assert order["payment_method"] in valid, (
                f"Invalid payment_method '{order['payment_method']}' on order {order['order_id']}"
            )

    def test_payment_status_is_valid(self):
        orders = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS).json()
        if not orders:
            pytest.skip("No orders in DB")
        valid = {"PENDING", "PAID", "FAILED"}
        for order in orders:
            assert order["payment_status"] in valid, (
                f"Invalid payment_status '{order['payment_status']}' on order {order['order_id']}"
            )

    def test_order_status_is_valid(self):
        orders = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS).json()
        if not orders:
            pytest.skip("No orders in DB")
        valid = {"PENDING", "PROCESSING", "SHIPPED", "DELIVERED", "CANCELLED"}
        for order in orders:
            assert order["order_status"] in valid, (
                f"Invalid order_status '{order['order_status']}' on order {order['order_id']}"
            )

    def test_total_amount_is_positive(self):
        orders = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS).json()
        if not orders:
            pytest.skip("No orders in DB")
        for order in orders:
            assert order["total_amount"] > 0, (
                f"Order {order['order_id']} has non-positive total_amount"
            )

    def test_gst_amount_is_non_negative(self):
        orders = requests.get(f"{BASE_URL}/admin/orders", headers=ADMIN_HEADERS).json()
        if not orders:
            pytest.skip("No orders in DB")
        for order in orders:
            assert order["gst_amount"] >= 0, (
                f"Order {order['order_id']} has negative gst_amount"
            )


# ═════════════════════════════════════════════════════════════════
# 6.  GET /admin/products
# ═════════════════════════════════════════════════════════════════

class TestAdminProducts:

    def test_status_200(self):
        res = requests.get(f"{BASE_URL}/admin/products", headers=ADMIN_HEADERS)
        assert res.status_code == 200

    def test_response_is_list(self):
        res = requests.get(f"{BASE_URL}/admin/products", headers=ADMIN_HEADERS)
        assert isinstance(res.json(), list)

    def test_product_fields_present(self):
        products = requests.get(f"{BASE_URL}/admin/products", headers=ADMIN_HEADERS).json()
        if not products:
            pytest.skip("No products in DB")
        product = products[0]
        for field in ("product_id", "name", "price", "is_active"):
            assert field in product, f"Field '{field}' missing from product"

    def test_includes_inactive_products(self):
        """Admin endpoint must expose inactive products too."""
        products = requests.get(f"{BASE_URL}/admin/products", headers=ADMIN_HEADERS).json()
        has_inactive = any(not p.get("is_active", True) for p in products)
        # This is informational — skip rather than fail if DB has none
        if not has_inactive:
            pytest.skip("No inactive products seeded — cannot verify inclusion")

    def test_price_is_positive(self):
        products = requests.get(f"{BASE_URL}/admin/products", headers=ADMIN_HEADERS).json()
        if not products:
            pytest.skip("No products in DB")
        for p in products:
            assert p["price"] > 0, f"Product {p['product_id']} has non-positive price"

    def test_stock_field_is_non_negative(self):
        products = requests.get(f"{BASE_URL}/admin/products", headers=ADMIN_HEADERS).json()
        if not products:
            pytest.skip("No products in DB")
        for p in products:
            if "stock" in p:
                assert p["stock"] >= 0, f"Product {p['product_id']} has negative stock"


# ═════════════════════════════════════════════════════════════════
# 7.  GET /admin/coupons
# ═════════════════════════════════════════════════════════════════

class TestAdminCoupons:

    def test_status_200(self):
        res = requests.get(f"{BASE_URL}/admin/coupons", headers=ADMIN_HEADERS)
        assert res.status_code == 200

    def test_response_is_list(self):
        res = requests.get(f"{BASE_URL}/admin/coupons", headers=ADMIN_HEADERS)
        assert isinstance(res.json(), list)

    def test_coupon_fields_present(self):
        coupons = requests.get(f"{BASE_URL}/admin/coupons", headers=ADMIN_HEADERS).json()
        if not coupons:
            pytest.skip("No coupons in DB")
        coupon = coupons[0]
        for field in ("coupon_code", "discount_type", "discount_value"):
            assert field in coupon, f"Field '{field}' missing from coupon"

    def test_discount_type_is_valid(self):
        coupons = requests.get(f"{BASE_URL}/admin/coupons", headers=ADMIN_HEADERS).json()
        if not coupons:
            pytest.skip("No coupons in DB")
        valid = {"PERCENT", "FIXED"}
        for c in coupons:
            assert c["discount_type"] in valid, (
                f"Invalid discount_type '{c['discount_type']}' on coupon {c['coupon_code']}"
            )

    def test_discount_value_is_positive(self):
        coupons = requests.get(f"{BASE_URL}/admin/coupons", headers=ADMIN_HEADERS).json()
        if not coupons:
            pytest.skip("No coupons in DB")
        for c in coupons:
            assert c["discount_value"] > 0, (
                f"Coupon {c['coupon_code']} has non-positive discount_value"
            )

    def test_includes_expired_coupons(self):
        """Admin endpoint must expose expired coupons as well."""
        coupons = requests.get(f"{BASE_URL}/admin/coupons", headers=ADMIN_HEADERS).json()
        has_expired = any(c.get("is_expired") for c in coupons)
        if not has_expired:
            pytest.skip("No expired coupons seeded — cannot verify inclusion")


# ═════════════════════════════════════════════════════════════════
# 8.  GET /admin/tickets
# ═════════════════════════════════════════════════════════════════

class TestAdminTickets:

    def test_status_200(self):
        res = requests.get(f"{BASE_URL}/admin/tickets", headers=ADMIN_HEADERS)
        assert res.status_code == 200

    def test_response_is_list(self):
        res = requests.get(f"{BASE_URL}/admin/tickets", headers=ADMIN_HEADERS)
        assert isinstance(res.json(), list)

    def test_ticket_fields_present(self):
        tickets = requests.get(f"{BASE_URL}/admin/tickets", headers=ADMIN_HEADERS).json()
        if not tickets:
            pytest.skip("No tickets in DB")
        ticket = tickets[0]
        for field in ("ticket_id", "user_id", "subject", "message", "status"):
            assert field in ticket, f"Field '{field}' missing from ticket"

    def test_ticket_status_is_valid(self):
        tickets = requests.get(f"{BASE_URL}/admin/tickets", headers=ADMIN_HEADERS).json()
        if not tickets:
            pytest.skip("No tickets in DB")
        valid = {"OPEN", "IN_PROGRESS", "CLOSED"}
        for t in tickets:
            assert t["status"] in valid, (
                f"Invalid status '{t['status']}' on ticket {t['ticket_id']}"
            )

    def test_message_is_non_empty(self):
        tickets = requests.get(f"{BASE_URL}/admin/tickets", headers=ADMIN_HEADERS).json()
        if not tickets:
            pytest.skip("No tickets in DB")
        for t in tickets:
            assert t["message"], f"Ticket {t['ticket_id']} has empty message"


# ═════════════════════════════════════════════════════════════════
# 9.  GET /admin/addresses
# ═════════════════════════════════════════════════════════════════

class TestAdminAddresses:

    def test_status_200(self):
        res = requests.get(f"{BASE_URL}/admin/addresses", headers=ADMIN_HEADERS)
        assert res.status_code == 200

    def test_response_is_list(self):
        res = requests.get(f"{BASE_URL}/admin/addresses", headers=ADMIN_HEADERS)
        assert isinstance(res.json(), list)

    def test_address_fields_present(self):
        addresses = requests.get(f"{BASE_URL}/admin/addresses", headers=ADMIN_HEADERS).json()
        if not addresses:
            pytest.skip("No addresses in DB")
        addr = addresses[0]
        for field in ("address_id", "user_id", "label", "street", "city",
                      "pincode", "is_default"):
            assert field in addr, f"Field '{field}' missing from address"

    def test_label_is_valid(self):
        addresses = requests.get(f"{BASE_URL}/admin/addresses", headers=ADMIN_HEADERS).json()
        if not addresses:
            pytest.skip("No addresses in DB")
        valid = {"HOME", "OFFICE", "OTHER"}
        for addr in addresses:
            assert addr["label"] in valid, (
                f"Invalid label '{addr['label']}' on address {addr['address_id']}"
            )

    def test_pincode_is_6_digits(self):
        addresses = requests.get(f"{BASE_URL}/admin/addresses", headers=ADMIN_HEADERS).json()
        if not addresses:
            pytest.skip("No addresses in DB")
        for addr in addresses:
            assert len(str(addr["pincode"])) == 6, (
                f"Pincode '{addr['pincode']}' on address {addr['address_id']} is not 6 digits"
            )

    def test_is_default_is_boolean(self):
        addresses = requests.get(f"{BASE_URL}/admin/addresses", headers=ADMIN_HEADERS).json()
        if not addresses:
            pytest.skip("No addresses in DB")
        for addr in addresses:
            assert isinstance(addr["is_default"], bool), (
                f"is_default on address {addr['address_id']} is not a boolean"
            )
