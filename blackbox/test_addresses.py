"""
QuickCart — Addresses Section Tests
Endpoints:
  GET    /api/v1/addresses
  POST   /api/v1/addresses
  PUT    /api/v1/addresses/{address_id}
  DELETE /api/v1/addresses/{address_id}

Run:
    pip install pytest requests
    pytest test_addresses.py -v
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

VALID_ADDRESS = {
    "label":      "HOME",
    "street":     "123 Test Street",
    "city":       "Hyderabad",
    "pincode":    "500001",
    "is_default": False,
}


@pytest.fixture(scope="session")
def valid_headers():
    return {"X-Roll-Number": ROLL, "X-User-ID": USER_ID}


@pytest.fixture
def created_address(valid_headers):
    """Create a fresh address and yield its id; delete after test."""
    res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers, json=VALID_ADDRESS)
    assert res.status_code in (200, 201)
    data = res.json()
    addr = data.get("address") or data
    addr_id = addr["address_id"]
    yield addr_id
    requests.delete(f"{BASE_URL}/addresses/{addr_id}", headers=valid_headers)


# ═════════════════════════════════════════════════════════════════
# 1. GET /api/v1/addresses
# ═════════════════════════════════════════════════════════════════

class TestGetAddresses:

    def test_valid_request_returns_200(self, valid_headers):
        res = requests.get(f"{BASE_URL}/addresses", headers=valid_headers)
        assert res.status_code == 200

    def test_response_is_list(self, valid_headers):
        res = requests.get(f"{BASE_URL}/addresses", headers=valid_headers)
        assert isinstance(res.json(), list)

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/addresses", USER_ID)

    def test_invalid_roll_number_returns_400(self):
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/addresses", USER_ID, "abc")

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/addresses", ROLL)

    def test_nonexistent_user_id_returns_400(self):
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/addresses", ROLL, "99999")


# ═════════════════════════════════════════════════════════════════
# 2. POST /api/v1/addresses
# ═════════════════════════════════════════════════════════════════

class TestPostAddress:

    def test_valid_address_created(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers, json=VALID_ADDRESS)
        assert res.status_code in (200, 201)
        data = res.json()
        addr = data.get("address") or data
        assert "address_id" in addr
        assert addr["label"] == VALID_ADDRESS["label"]
        requests.delete(f"{BASE_URL}/addresses/{addr['address_id']}", headers=valid_headers)

    def test_invalid_label_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                            json={**VALID_ADDRESS, "label": "WORK"})
        assert res.status_code == 400

    def test_street_too_short_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                            json={**VALID_ADDRESS, "street": "abc"})
        assert res.status_code == 400

    def test_street_too_long_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                            json={**VALID_ADDRESS, "street": "A" * 101})
        assert res.status_code == 400

    def test_city_too_short_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                            json={**VALID_ADDRESS, "city": "A"})
        assert res.status_code == 400

    def test_city_too_long_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                            json={**VALID_ADDRESS, "city": "A" * 51})
        assert res.status_code == 400

    def test_pincode_5_digits_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                            json={**VALID_ADDRESS, "pincode": "50001"})
        assert res.status_code == 400

    def test_pincode_7_digits_returns_400(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                            json={**VALID_ADDRESS, "pincode": "5000011"})
        assert res.status_code == 400

    def test_only_one_default_at_a_time(self, valid_headers):
        """Setting a new default must unset the previous default."""
        r1 = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                           json={**VALID_ADDRESS, "is_default": True}).json()
        addr1 = r1.get("address") or r1
        r2 = requests.post(f"{BASE_URL}/addresses", headers=valid_headers,
                           json={**VALID_ADDRESS, "label": "OFFICE", "is_default": True}).json()
        addr2 = r2.get("address") or r2

        all_addrs = requests.get(f"{BASE_URL}/addresses", headers=valid_headers).json()
        a1 = next((a for a in all_addrs if a["address_id"] == addr1["address_id"]), None)
        assert a1 is not None and not a1["is_default"], "Previous default was not unset"

        requests.delete(f"{BASE_URL}/addresses/{addr1['address_id']}", headers=valid_headers)
        requests.delete(f"{BASE_URL}/addresses/{addr2['address_id']}", headers=valid_headers)

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/addresses", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/addresses", ROLL)


# ═════════════════════════════════════════════════════════════════
# 3. PUT /api/v1/addresses/{address_id}
# ═════════════════════════════════════════════════════════════════

class TestPutAddress:

    def test_update_street_returns_200(self, valid_headers, created_address):
        res = requests.put(f"{BASE_URL}/addresses/{created_address}", headers=valid_headers,
                           json={"street": "456 Updated Road Lane"})
        assert res.status_code == 200

    def test_response_shows_updated_street(self, valid_headers, created_address):
        new_street = "789 New Avenue Block"
        res = requests.put(f"{BASE_URL}/addresses/{created_address}", headers=valid_headers,
                           json={"street": new_street})
        data = res.json()
        addr = data.get("address") or data
        assert addr["street"] == new_street, (
            f"Response still shows old street: {addr.get('street')}"
        )

    def test_update_is_default_to_true(self, valid_headers, created_address):
        res = requests.put(f"{BASE_URL}/addresses/{created_address}", headers=valid_headers,
                           json={"is_default": True})
        assert res.status_code == 200

    def test_update_nonexistent_address_returns_404(self, valid_headers):
        res = requests.put(f"{BASE_URL}/addresses/999999", headers=valid_headers,
                           json={"street": "No Such Street 99"})
        assert res.status_code == 404

    def test_missing_roll_number_returns_401(self, created_address):
        assert_missing_roll_number_returns_401(
            f"{BASE_URL}/addresses/{created_address}", USER_ID)

    def test_missing_user_id_returns_400(self, created_address):
        assert_missing_user_id_returns_400(
            f"{BASE_URL}/addresses/{created_address}", ROLL)


# ═════════════════════════════════════════════════════════════════
# 4. DELETE /api/v1/addresses/{address_id}
# ═════════════════════════════════════════════════════════════════

class TestDeleteAddress:

    def test_delete_existing_address_returns_200(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers, json=VALID_ADDRESS)
        addr = (res.json().get("address") or res.json())
        del_res = requests.delete(f"{BASE_URL}/addresses/{addr['address_id']}", headers=valid_headers)
        assert del_res.status_code == 200

    def test_delete_nonexistent_address_returns_404(self, valid_headers):
        res = requests.delete(f"{BASE_URL}/addresses/999999", headers=valid_headers)
        assert res.status_code == 404

    def test_address_gone_after_delete(self, valid_headers):
        res = requests.post(f"{BASE_URL}/addresses", headers=valid_headers, json=VALID_ADDRESS)
        addr = (res.json().get("address") or res.json())
        addr_id = addr["address_id"]
        requests.delete(f"{BASE_URL}/addresses/{addr_id}", headers=valid_headers)
        all_addrs = requests.get(f"{BASE_URL}/addresses", headers=valid_headers).json()
        assert addr_id not in [a["address_id"] for a in all_addrs]

    def test_missing_roll_number_returns_401(self):
        assert_missing_roll_number_returns_401(f"{BASE_URL}/addresses/1", USER_ID)

    def test_missing_user_id_returns_400(self):
        assert_missing_user_id_returns_400(f"{BASE_URL}/addresses/1", ROLL)
