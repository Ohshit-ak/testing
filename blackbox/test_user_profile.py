"""
QuickCart — Profile Section Tests
Endpoints: GET /api/v1/profile  |  PUT /api/v1/profile

Run:
    pip install pytest requests
    pytest test_profile.py -v
"""

import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"
ROLL     = "2024111004"   # ← replace with your roll number
USER_ID  = "1"       # ← replace with a valid user ID from GET /admin/users


# ── fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def valid_headers():
    return {
        "X-Roll-Number": ROLL,
        "X-User-ID":     USER_ID,
    }

@pytest.fixture
def valid_put_headers():
    return {
        "X-Roll-Number": ROLL,
        "X-User-ID":     USER_ID,
    }


# ═════════════════════════════════════════════════════════════════
# 1. GET /api/v1/profile
# ═════════════════════════════════════════════════════════════════

class TestGetProfile:

    def test_valid_request_returns_200(self, valid_headers):
        res = requests.get(f"{BASE_URL}/profile", headers=valid_headers)
        assert res.status_code == 200

    def test_missing_roll_number_returns_401(self):
        res = requests.get(f"{BASE_URL}/profile", headers={
            "X-User-ID": USER_ID
        })
        assert res.status_code == 401

    def test_non_integer_roll_number_letters_returns_400(self):
        res = requests.get(f"{BASE_URL}/profile", headers={
            "X-Roll-Number": "abc",
            "X-User-ID":     USER_ID,
        })
        assert res.status_code == 400

    def test_non_integer_roll_number_symbols_returns_400(self):
        res = requests.get(f"{BASE_URL}/profile", headers={
            "X-Roll-Number": "##!",
            "X-User-ID":     USER_ID,
        })
        assert res.status_code == 400

    def test_missing_user_id_returns_400(self):
        res = requests.get(f"{BASE_URL}/profile", headers={
            "X-Roll-Number": ROLL
        })
        assert res.status_code == 400

    def test_user_id_zero_returns_400(self):
        res = requests.get(f"{BASE_URL}/profile", headers={
            "X-Roll-Number": ROLL,
            "X-User-ID":     "0",
        })
        assert res.status_code == 400

    def test_user_id_negative_returns_400(self):
        res = requests.get(f"{BASE_URL}/profile", headers={
            "X-Roll-Number": ROLL,
            "X-User-ID":     "-1",
        })
        assert res.status_code == 400

    def test_non_existent_user_id_returns_400(self):
        res = requests.get(f"{BASE_URL}/profile", headers={
            "X-Roll-Number": ROLL,
            "X-User-ID":     "99999999",
        })
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════
# 2. PUT /api/v1/profile — valid updates
# ═════════════════════════════════════════════════════════════════

class TestPutProfileValid:

    def test_valid_name_and_phone_returns_200(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Alice Kumar", "phone": "9876543210"})
        assert res.status_code == 200

    def test_name_min_boundary_2_chars_returns_200(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Ab", "phone": "9876543210"})
        assert res.status_code == 200

    def test_name_max_boundary_50_chars_returns_200(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "A" * 50, "phone": "9876543210"})
        assert res.status_code == 200


# ═════════════════════════════════════════════════════════════════
# 3. PUT /api/v1/profile — name validation
# ═════════════════════════════════════════════════════════════════

class TestPutProfileNameValidation:

    def test_name_1_char_below_min_returns_400(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "A", "phone": "9876543210"})
        assert res.status_code == 400

    def test_name_51_chars_above_max_returns_400(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "A" * 51, "phone": "9876543210"})
        assert res.status_code == 400

    def test_name_empty_string_returns_400(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "", "phone": "9876543210"})
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════
# 4. PUT /api/v1/profile — phone validation
# ═════════════════════════════════════════════════════════════════

class TestPutProfilePhoneValidation:

    def test_phone_9_digits_too_short_returns_400(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Alice", "phone": "987654321"})
        assert res.status_code == 400

    def test_phone_11_digits_too_long_returns_400(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Alice", "phone": "98765432101"})
        assert res.status_code == 400

    def test_phone_letters_returns_400(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Alice", "phone": "abcdefghij"})
        assert res.status_code == 400

    def test_phone_empty_string_returns_400(self, valid_put_headers):
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Alice", "phone": ""})
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════
# 5. PUT /api/v1/profile — header checks
# ═════════════════════════════════════════════════════════════════

class TestPutProfileHeaders:

    def test_missing_roll_number_returns_401(self):
        res = requests.put(f"{BASE_URL}/profile",
                           headers={"Content-Type": "application/json", "X-User-ID": USER_ID},
                           json={"name": "Alice", "phone": "9876543210"})
        assert res.status_code == 401

    def test_non_integer_roll_number_returns_400(self):
        res = requests.put(f"{BASE_URL}/profile",
                           headers={"Content-Type": "application/json",
                                    "X-Roll-Number": "xyz", "X-User-ID": USER_ID},
                           json={"name": "Alice", "phone": "9876543210"})
        assert res.status_code == 400

    def test_missing_user_id_returns_400(self):
        res = requests.put(f"{BASE_URL}/profile",
                           headers={"Content-Type": "application/json", "X-Roll-Number": ROLL},
                           json={"name": "Alice", "phone": "9876543210"})
        assert res.status_code == 400

    def test_non_existent_user_id_returns_400(self):
        res = requests.put(f"{BASE_URL}/profile",
                           headers={"Content-Type": "application/json",
                                    "X-Roll-Number": ROLL, "X-User-ID": "99999"},
                           json={"name": "Alice", "phone": "9876543210"})
        assert res.status_code == 400