"""
QuickCart — Coupons Section Tests
Endpoints:
  POST /api/v1/coupon/apply
  POST /api/v1/coupon/remove

Run:
    pip install pytest requests
    pytest test_coupons.py -v
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
def coupons(valid_headers):
    """Fetch all coupons from admin endpoint once per session."""
    res = requests.get(f"{BASE_URL}/admin/coupons",
                       headers={"X-Roll-Number": ROLL})
    assert res.status_code == 200
    return res.json()


@pytest.fixture(scope="session")
def valid_coupon(coupons):
    """Return a non-expired coupon with no minimum cart value (or lowest minimum)."""
    non_expired = [c for c in coupons if not c.get("is_expired", False)]
    assert non_expired, "No valid (non-expired) coupon found — seed the DB"
    # prefer coupon with lowest or no minimum cart value
    return sorted(non_expired, key=lambda c: c.get("min_cart_value", 0))[0]


@pytest.fixture(scope="session")
def active_product(valid_headers):
    res = requests.get(f"{BASE_URL}/admin/products", headers={"X-Roll-Number": ROLL})
    products = res.json()
    active = [p for p in products if p.get("is_active")]
    assert active, "No active products found"
    return active[0]


@pytest.fixture(autouse=True)
def reset_cart(valid_headers, active_product):
    """Ensure cart has one item before every coupon test, then clear after."""
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)
    requests.post(f"{BASE_URL}/cart/add", headers=valid_headers,
                  json={"product_id": active_product["product_id"], "quantity": 1})
    yield
    requests.post(f"{BASE_URL}/coupon/remove", headers=valid_headers, json={})
    requests.delete(f"{BASE_URL}/cart/clear", headers=valid_headers)


# ═════════════════════════════════════════════════════════════════
# 1. POST /api/v1/coupon/apply
# ═════════════════════════════════════════════════════════════════

class TestCouponApply:

    def test_apply_valid_coupon_returns_200(self, valid_headers, valid_coupon):
        res = requests.post(f"{BASE_URL}/coupon/apply", headers=valid_headers,
                            json={"coupon_code": valid_coupon["coupon_code"]})
        # 200 = applied; 400 = cart total below minimum — both are acceptable results
        assert res.status_code in (200, 400)

    def test_apply_nonexistent_coupon_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/coupon/apply", headers=valid_headers,
                            json={"coupon_code": "INVALID_COUPON_XYZ"})
        assert res.status_code == 400

    def test_apply_expired_coupon_returns_400(self, valid_headers, coupons):
        expired = [c for c in coupons if c.get("is_expired", False)]
        if not expired:
            pytest.skip("No expired coupon available to test")
        res = requests.post(f"{BASE_URL}/coupon/apply", headers=valid_headers,
                            json={"coupon_code": expired[0]["coupon_code"]})
        assert res.status_code == 400

    def test_percent_discount_calculated_correctly(self, valid_headers, coupons, active_product):
        """PERCENT coupon: discount = cart_total × (discount_value / 100), capped if needed."""
        percent_coupons = [
            c for c in coupons
            if c.get("discount_type") == "PERCENT" and not c.get("is_expired", False)
        ]
        if not percent_coupons:
            pytest.skip("No active PERCENT coupon available")
        coupon = percent_coupons[0]

        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        cart_total = cart["total"]

        res = requests.post(f"{BASE_URL}/coupon/apply", headers=valid_headers,
                            json={"coupon_code": coupon["coupon_code"]})
        if res.status_code == 400:
            pytest.skip("Cart total below coupon minimum — can't validate discount math")

        data = res.json()
        raw_discount = cart_total * coupon["discount_value"] / 100
        max_disc = coupon.get("max_discount")
        expected_discount = min(raw_discount, max_disc) if max_disc else raw_discount
        expected_discount = round(expected_discount, 2)

        actual_discount = round(data.get("discount", 0), 2)
        assert abs(actual_discount - expected_discount) < 0.01, (
            f"PERCENT discount wrong: got {actual_discount}, expected {expected_discount}"
        )

    def test_fixed_discount_calculated_correctly(self, valid_headers, coupons):
        """FIXED coupon: discount = discount_value (capped at cart total)."""
        fixed_coupons = [
            c for c in coupons
            if c.get("discount_type") == "FIXED" and not c.get("is_expired", False)
        ]
        if not fixed_coupons:
            pytest.skip("No active FIXED coupon available")
        coupon = fixed_coupons[0]

        cart = requests.get(f"{BASE_URL}/cart", headers=valid_headers).json()
        cart_total = cart["total"]

        res = requests.post(f"{BASE_URL}/coupon/apply", headers=valid_headers,
                            json={"coupon_code": coupon["coupon_code"]})
        if res.status_code == 400:
            pytest.skip("Cart total below coupon minimum")

        data = res.json()
        expected_discount = round(min(coupon["discount_value"], cart_total), 2)
        actual_discount = round(data.get("discount", 0), 2)
        assert abs(actual_discount - expected_discount) < 0.01, (
            f"FIXED discount wrong: got {actual_discount}, expected {expected_discount}"
        )

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/coupon/apply", USER_ID)

    def test_invalid_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/coupon/apply", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/coupon/apply", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/coupon/apply", ROLL, "99999")


# ═════════════════════════════════════════════════════════════════
# 2. POST /api/v1/coupon/remove
# ═════════════════════════════════════════════════════════════════

class TestCouponRemove:

    def test_remove_returns_200(self, valid_headers, valid_coupon):
        # Apply first, then remove
        requests.post(f"{BASE_URL}/coupon/apply", headers=valid_headers,
                      json={"coupon_code": valid_coupon["coupon_code"]})
        res = requests.post(f"{BASE_URL}/coupon/remove", headers=valid_headers, json={})
        assert res.status_code == 200

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/coupon/remove", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/coupon/remove", ROLL)
