"""
QuickCart — Wallet Section Tests
Endpoints:
  GET  /api/v1/wallet
  POST /api/v1/wallet/add
  POST /api/v1/wallet/pay

Run:
    pip install pytest requests
    pytest test_wallet.py -v
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


def get_balance(headers):
    return requests.get(f"{BASE_URL}/wallet", headers=headers).json().get("balance", 0)


# ═════════════════════════════════════════════════════════════════
# 1. GET /api/v1/wallet
# ═════════════════════════════════════════════════════════════════

class TestGetWallet:

    def test_valid_request_returns_200(self, valid_headers):
        res = requests.get(f"{BASE_URL}/wallet", headers=valid_headers)
        assert res.status_code == 200

    def test_response_has_balance_field(self, valid_headers):
        res = requests.get(f"{BASE_URL}/wallet", headers=valid_headers)
        assert "balance" in res.json()

    def test_balance_is_numeric(self, valid_headers):
        res = requests.get(f"{BASE_URL}/wallet", headers=valid_headers)
        assert isinstance(res.json()["balance"], (int, float))

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/wallet", USER_ID)

    def test_invalid_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/wallet", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/wallet", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/wallet", ROLL, "99999")


# ═════════════════════════════════════════════════════════════════
# 2. POST /api/v1/wallet/add
# ═════════════════════════════════════════════════════════════════

class TestWalletAdd:

    def test_add_valid_amount_returns_200(self, valid_headers):
        res = requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers,
                            json={"amount": 100})
        assert res.status_code == 200

    def test_balance_increases_after_add(self, valid_headers):
        before = get_balance(valid_headers)
        requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers, json={"amount": 50})
        after = get_balance(valid_headers)
        assert round(after - before, 2) == 50.0, (
            f"Balance did not increase by 50: before={before}, after={after}"
        )

    def test_add_zero_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers,
                            json={"amount": 0})
        assert res.status_code == 400

    def test_add_negative_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers,
                            json={"amount": -100})
        assert res.status_code == 400

    def test_add_over_max_100000_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers,
                            json={"amount": 100001})
        assert res.status_code == 400

    def test_add_exactly_100000_returns_200(self, valid_headers):
        res = requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers,
                            json={"amount": 100000})
        assert res.status_code == 200

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/wallet/add", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/wallet/add", ROLL)


# ═════════════════════════════════════════════════════════════════
# 3. POST /api/v1/wallet/pay
# ═════════════════════════════════════════════════════════════════

class TestWalletPay:

    def test_pay_valid_amount_returns_200(self, valid_headers):
        # Ensure there's enough balance
        requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers, json={"amount": 500})
        res = requests.post(f"{BASE_URL}/wallet/pay", headers=valid_headers,
                            json={"amount": 100})
        assert res.status_code == 200

    def test_balance_decreases_by_exact_amount(self, valid_headers):
        requests.post(f"{BASE_URL}/wallet/add", headers=valid_headers, json={"amount": 500})
        before = get_balance(valid_headers)
        pay_amount = 75
        requests.post(f"{BASE_URL}/wallet/pay", headers=valid_headers,
                      json={"amount": pay_amount})
        after = get_balance(valid_headers)
        assert round(before - after, 2) == pay_amount, (
            f"Balance should decrease by exactly {pay_amount}: before={before}, after={after}"
        )

    def test_pay_zero_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/wallet/pay", headers=valid_headers,
                            json={"amount": 0})
        assert res.status_code == 400

    def test_pay_negative_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/wallet/pay", headers=valid_headers,
                            json={"amount": -50})
        assert res.status_code == 400

    def test_pay_more_than_balance_returns_400(self, valid_headers):
        balance = get_balance(valid_headers)
        res = requests.post(f"{BASE_URL}/wallet/pay", headers=valid_headers,
                            json={"amount": balance + 9999})
        assert res.status_code == 400

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/wallet/pay", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/wallet/pay", ROLL)
