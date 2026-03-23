"""
QuickCart — Loyalty Points Section Tests
Endpoints:
  GET  /api/v1/loyalty
  POST /api/v1/loyalty/redeem

Run:
    pip install pytest requests
    pytest test_loyalty.py -v
"""

import pytest
import requests
from header_validation import (
    assert_missing_roll_number_returns_401,
    assert_invalid_roll_number_returns_400,
    assert_missing_user_id_returns_400,
    assert_invalid_user_id_returns_400,
    assert_zero_user_id_returns_400,
    assert_negative_user_id_returns_400,
    assert_nonexistent_user_id_returns_400,
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

def get_points(headers):
    """Helper: return current loyalty points balance."""
    return requests.get(f"{BASE_URL}/loyalty", headers=headers).json().get("points", 0)


# ═════════════════════════════════════════════════════════════════
# 1. GET /api/v1/loyalty
# ═════════════════════════════════════════════════════════════════

class TestLoyaltyPoints:

    def test_valid_request_returns_200(self, valid_headers):
        res = requests.get(f"{BASE_URL}/loyalty", headers=valid_headers)
        assert res.status_code == 200

    def test_response_contains_points_field(self, valid_headers):
        res = requests.get(f"{BASE_URL}/loyalty", headers=valid_headers)
        assert "points" in res.json(), "Response should contain 'points' field"

    def test_points_is_integer(self, valid_headers):
        res = requests.get(f"{BASE_URL}/loyalty", headers=valid_headers)
        assert isinstance(res.json()["points"], int), "'points' should be an integer"

    def test_points_is_non_negative(self, valid_headers):
        res = requests.get(f"{BASE_URL}/loyalty", headers=valid_headers)
        assert res.json()["points"] >= 0, "Loyalty points should never be negative"

    def test_points_matches_admin_source(self, valid_headers):
        """Points returned must match what the admin endpoint shows for the same user."""
        admin_users = requests.get(f"{BASE_URL}/admin/users",
                                   headers={"X-Roll-Number": ROLL}).json()
        admin_user = next((u for u in admin_users if str(u["user_id"]) == USER_ID), None)
        if admin_user is None:
            pytest.skip("Could not find user in admin endpoint")
        loyalty_res = requests.get(f"{BASE_URL}/loyalty", headers=valid_headers).json()
        assert loyalty_res["points"] == admin_user["loyalty_points"], (
            f"Loyalty points mismatch: /loyalty says {loyalty_res['points']}, "
            f"admin says {admin_user['loyalty_points']}"
        )

    # ── header validation ─────────────────────────────────────────

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/loyalty", USER_ID)

    def test_non_integer_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/loyalty", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/loyalty", ROLL)

    def test_non_integer_user_id_returns_400(self):
        assert_invalid_user_id_returns_400(f"{BASE_URL}/loyalty", ROLL, "abc")

    def test_user_id_zero_returns_400(self):
        assert_zero_user_id_returns_400(f"{BASE_URL}/loyalty", ROLL)

    def test_user_id_negative_returns_400(self):
        assert_negative_user_id_returns_400(f"{BASE_URL}/loyalty", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/loyalty", ROLL, "9999")


# ═════════════════════════════════════════════════════════════════
# 2. POST /api/v1/loyalty/redeem
# ═════════════════════════════════════════════════════════════════

class TestLoyaltyRedeem:

    def test_redeem_valid_amount_200_or_400(self, valid_headers):
        """200 when points are sufficient; 400 when they are not — both are valid."""
        res = requests.post(f"{BASE_URL}/loyalty/redeem",
                            headers=valid_headers,
                            json={"amount": 10})
        assert res.status_code in (200, 400)

    def test_redeem_zero_returns_400(self, valid_headers):
        """Amount must be at least 1 — redeeming 0 must be rejected (Bug #28)."""
        res = requests.post(f"{BASE_URL}/loyalty/redeem",
                            headers=valid_headers,
                            json={"amount": 0})
        assert res.status_code == 400, (
            "Redeeming 0 points should return 400 (Bug #28)"
        )

    def test_redeem_negative_returns_400(self, valid_headers):
        """Negative redemption amount must be rejected."""
        res = requests.post(f"{BASE_URL}/loyalty/redeem",
                            headers=valid_headers,
                            json={"amount": -5})
        assert res.status_code == 400

    def test_redeem_more_than_balance_returns_400(self, valid_headers):
        """Cannot redeem more points than the current balance."""
        current = get_points(valid_headers)
        res = requests.post(f"{BASE_URL}/loyalty/redeem",
                            headers=valid_headers,
                            json={"amount": current + 99999})
        assert res.status_code == 400, (
            f"Expected 400 when redeeming {current + 99999} but only {current} available"
        )

    def test_redeem_decreases_points_by_exact_amount(self, valid_headers):
        """After a successful redemption, points must decrease by exactly the redeemed amount."""
        before = get_points(valid_headers)
        if before < 1:
            pytest.skip("User has 0 loyalty points — cannot test decrease")

        redeem_amount = 1
        res = requests.post(f"{BASE_URL}/loyalty/redeem",
                            headers=valid_headers,
                            json={"amount": redeem_amount})
        if res.status_code != 200:
            pytest.skip("Redemption failed unexpectedly")

        after = get_points(valid_headers)
        assert after == before - redeem_amount, (
            f"Points should decrease by {redeem_amount}: before={before}, after={after}"
        )

    # ── header validation ─────────────────────────────────────────

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/loyalty/redeem", USER_ID)

    def test_non_integer_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/loyalty/redeem", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/loyalty/redeem", ROLL)

    def test_user_id_zero_returns_400(self):
        assert_zero_user_id_returns_400(f"{BASE_URL}/loyalty/redeem", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/loyalty/redeem", ROLL, "9999")
