"""
QuickCart — Profile Section Tests
Endpoints: GET /api/v1/profile  |  PUT /api/v1/profile

Run:
    pip install pytest requests
    pytest test_user_profile.py -v
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
USER_ID  = "1"            # ← replace with a valid user ID from GET /admin/users


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

    def test_response_contains_user_id(self, valid_headers):
        res = requests.get(f"{BASE_URL}/profile", headers=valid_headers)
        assert "user_id" in res.json(), "Response missing 'user_id'"

    def test_response_contains_name(self, valid_headers):
        res = requests.get(f"{BASE_URL}/profile", headers=valid_headers)
        assert "name" in res.json(), "Response missing 'name'"

    def test_response_contains_phone(self, valid_headers):
        res = requests.get(f"{BASE_URL}/profile", headers=valid_headers)
        assert "phone" in res.json(), "Response missing 'phone'"

    def test_returned_user_id_matches_header(self, valid_headers):
        res = requests.get(f"{BASE_URL}/profile", headers=valid_headers)
        assert str(res.json().get("user_id")) == USER_ID, (
            f"Returned user_id does not match X-User-ID header"
        )

    # ── header validation ─────────────────────────────────────────

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/profile", USER_ID)

    def test_non_integer_roll_number_letters_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/profile", USER_ID, "abc")

    def test_non_integer_roll_number_symbols_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/profile", USER_ID, "##!@")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/profile", ROLL)

    def test_user_id_zero_returns_400(self):
        assert_zero_user_id_returns_400(f"{BASE_URL}/profile", ROLL)

    def test_user_id_negative_returns_400(self):
        assert_negative_user_id_returns_400(f"{BASE_URL}/profile", ROLL)

    def test_non_existent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/profile", ROLL, "99999999")


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

    def test_update_is_persisted(self, valid_put_headers, valid_headers):
        """Changes made via PUT must be visible on the next GET."""
        new_name = "PersistenceCheck"
        requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                     json={"name": new_name, "phone": "9000000001"})
        res = requests.get(f"{BASE_URL}/profile", headers=valid_headers)
        assert res.json().get("name") == new_name, (
            f"Profile update not persisted. Got: {res.json().get('name')}"
        )


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

    def test_phone_with_hyphens_returns_400(self, valid_put_headers):
        """10 characters but contains a hyphen — must be rejected (Bug #2)."""
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Alice", "phone": "98765-3210"})
        assert res.status_code == 400, (
            "Phone '98765-3210' has non-digit chars but was accepted (Bug #2)"
        )

    def test_phone_with_spaces_returns_400(self, valid_put_headers):
        """Phone with spaces must be rejected even if digit count is 10."""
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Alice", "phone": "98765 3210"})
        assert res.status_code == 400

    def test_phone_with_plus_prefix_returns_400(self, valid_put_headers):
        """E.164-style prefix (+91) must be rejected — only 10 bare digits allowed."""
        res = requests.put(f"{BASE_URL}/profile", headers=valid_put_headers,
                           json={"name": "Alice", "phone": "+919876543"})
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════
# 5. PUT /api/v1/profile — header checks
# ═════════════════════════════════════════════════════════════════

class TestPutProfileHeaders:

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/profile", USER_ID)

    def test_non_integer_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/profile", USER_ID, "xyz")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/profile", ROLL)

    def test_non_existent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/profile", ROLL, "99999")
