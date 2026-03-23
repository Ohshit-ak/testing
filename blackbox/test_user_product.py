"""
QuickCart — Products Section Tests
Endpoints:
  GET /api/v1/products
  GET /api/v1/products/{product_id}

Run:
    pip install pytest requests
    pytest test_products.py -v
"""

import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"
ROLL     = "12345"   # ← replace with your roll number
USER_ID  = "1"       # ← replace with a valid user ID


# ── fixtures ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def valid_headers():
    return {
        "X-Roll-Number": ROLL,
        "X-User-ID":     USER_ID,
    }

@pytest.fixture(scope="session")
def admin_products(valid_headers):
    """
    Fetch the full product list (active + inactive) from the admin endpoint
    once per test session. All tests derive their test data from this.
    """
    res = requests.get(f"{BASE_URL}/admin/products",
                       headers={"X-Roll-Number": ROLL})
    assert res.status_code == 200, "Could not fetch /admin/products — check server and ROLL"
    products = res.json()
    assert len(products) > 0, "No products in DB — seed the server first"
    return products

@pytest.fixture(scope="session")
def active_product(admin_products):
    """First product that is active."""
    p = next((p for p in admin_products if p.get("is_active") or p.get("active")), None)
    assert p is not None, "No active product found — seed an active product first"
    return p

@pytest.fixture(scope="session")
def inactive_product(admin_products):
    """First product that is inactive."""
    p = next((p for p in admin_products if not (p.get("is_active") or p.get("active"))), None)
    assert p is not None, "No inactive product found — seed an inactive product first"
    return p


# ═════════════════════════════════════════════════════════════════
# 1. GET /api/v1/products  — product listing
# ═════════════════════════════════════════════════════════════════

class TestGetProducts:

    def test_valid_request_returns_200(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products", headers=valid_headers)
        assert res.status_code == 200

    def test_response_is_a_list(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products", headers=valid_headers)
        assert isinstance(res.json(), list)

    # ── active / inactive visibility ─────────────────────────────

    def test_only_active_products_returned(self, valid_headers, admin_products):
        res = requests.get(f"{BASE_URL}/products", headers=valid_headers)
        returned_ids = {p["product_id"] for p in res.json()}
        for p in admin_products:
            is_active = p.get("is_active") or p.get("active")
            if is_active:
                assert p["product_id"] in returned_ids, (
                    f"Active product {p['product_id']} missing from listing"
                )
            else:
                assert p["product_id"] not in returned_ids, (
                    f"Inactive product {p['product_id']} should not appear in listing"
                )

    def test_inactive_product_not_in_listing(self, valid_headers, inactive_product):
        res = requests.get(f"{BASE_URL}/products", headers=valid_headers)
        returned_ids = {p["product_id"] for p in res.json()}
        assert inactive_product["product_id"] not in returned_ids

    # ── price accuracy ────────────────────────────────────────────

    def test_prices_match_admin_source(self, valid_headers, admin_products):
        """Prices returned in the listing must exactly match the DB values."""
        admin_price = {p["product_id"]: p["price"] for p in admin_products}
        res = requests.get(f"{BASE_URL}/products", headers=valid_headers)
        for p in res.json():
            assert p["price"] == admin_price[p["product_id"]], (
                f"Price mismatch for product {p['product_id']}: "
                f"got {p['price']}, expected {admin_price[p['product_id']]}"
            )

    # ── filter by category ────────────────────────────────────────

    def test_filter_by_category_returns_only_that_category(self, valid_headers, admin_products):
        active = [p for p in admin_products if p.get("is_active") or p.get("active")]
        if not active or not active[0].get("category"):
            pytest.skip("No categorised active products available")

        category = active[0]["category"]
        res = requests.get(f"{BASE_URL}/products",
                           headers=valid_headers,
                           params={"category": category})
        assert res.status_code == 200
        for p in res.json():
            assert p["category"] == category, (
                f"Product {p['product_id']} has category '{p['category']}', expected '{category}'"
            )

    def test_filter_by_nonexistent_category_returns_empty(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products",
                           headers=valid_headers,
                           params={"category": "NONEXISTENT_XYZ_CATEGORY"})
        assert res.status_code == 200
        assert res.json() == []

    # ── search by name ────────────────────────────────────────────

    def test_search_by_name_returns_matching_products(self, valid_headers, active_product):
        # Use first 3 chars of an active product name as search term
        search_term = active_product["name"][:3]
        res = requests.get(f"{BASE_URL}/products",
                           headers=valid_headers,
                           params={"search": search_term})
        assert res.status_code == 200
        results = res.json()
        assert len(results) > 0, f"Expected at least one result for search '{search_term}'"
        for p in results:
            assert search_term.lower() in p["name"].lower(), (
                f"Product '{p['name']}' does not match search term '{search_term}'"
            )

    def test_search_with_no_match_returns_empty(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products",
                           headers=valid_headers,
                           params={"search": "ZZZNOMATCHZZZ"})
        assert res.status_code == 200
        assert res.json() == []

    # ── sort by price ─────────────────────────────────────────────

    def test_sort_price_ascending(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products",
                           headers=valid_headers,
                           params={"sort": "price_asc"})
        assert res.status_code == 200
        prices = [p["price"] for p in res.json()]
        assert prices == sorted(prices), "Products are not sorted by price ascending"

    def test_sort_price_descending(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products",
                           headers=valid_headers,
                           params={"sort": "price_desc"})
        assert res.status_code == 200
        prices = [p["price"] for p in res.json()]
        assert prices == sorted(prices, reverse=True), (
            "Products are not sorted by price descending"
        )

    # ── header checks ─────────────────────────────────────────────

    def test_missing_roll_number_returns_401(self):
        res = requests.get(f"{BASE_URL}/products",
                           headers={"X-User-ID": USER_ID})
        assert res.status_code == 401

    def test_non_integer_roll_number_returns_400(self):
        res = requests.get(f"{BASE_URL}/products",
                           headers={"X-Roll-Number": "abc", "X-User-ID": USER_ID})
        assert res.status_code == 400

    def test_missing_user_id_returns_400(self):
        res = requests.get(f"{BASE_URL}/products",
                           headers={"X-Roll-Number": ROLL})
        assert res.status_code == 400

    def test_invalid_user_id_zero_returns_400(self):
        res = requests.get(f"{BASE_URL}/products",
                           headers={"X-Roll-Number": ROLL, "X-User-ID": "0"})
        assert res.status_code == 400

    def test_non_existent_user_id_returns_400(self):
        res = requests.get(f"{BASE_URL}/products",
                           headers={"X-Roll-Number": ROLL, "X-User-ID": "99999"})
        assert res.status_code == 400


# ═════════════════════════════════════════════════════════════════
# 2. GET /api/v1/products/{product_id}  — single product lookup
# ═════════════════════════════════════════════════════════════════

class TestGetProductById:

    # ── happy path ────────────────────────────────────────────────

    def test_valid_active_product_returns_200(self, valid_headers, active_product):
        res = requests.get(f"{BASE_URL}/products/{active_product['product_id']}",
                           headers=valid_headers)
        assert res.status_code == 200

    def test_response_contains_correct_id(self, valid_headers, active_product):
        res = requests.get(f"{BASE_URL}/products/{active_product['product_id']}",
                           headers=valid_headers)
        assert res.json()["product_id"] == active_product["product_id"]

    def test_price_matches_admin_source(self, valid_headers, active_product):
        res = requests.get(f"{BASE_URL}/products/{active_product['product_id']}",
                           headers=valid_headers)
        assert res.json()["price"] == active_product["price"], (
            f"Price mismatch: got {res.json()['price']}, "
            f"expected {active_product['price']}"
        )

    # ── inactive product ──────────────────────────────────────────

    def test_inactive_product_by_id_returns_404(self, valid_headers, inactive_product):
        """
        The listing hides inactive products; looking one up by ID should
        also return 404 (adjust expected status if the server behaves differently).
        """
        res = requests.get(f"{BASE_URL}/products/{inactive_product['product_id']}",
                           headers=valid_headers)
        assert res.status_code == 404

    # ── not found ─────────────────────────────────────────────────

    def test_nonexistent_product_id_returns_404(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products/999999",
                           headers=valid_headers)
        assert res.status_code == 404

    def test_string_product_id_returns_404_or_400(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products/abc",
                           headers=valid_headers)
        assert res.status_code in (400, 404)

    # ── header checks ─────────────────────────────────────────────

    def test_missing_roll_number_returns_401(self, active_product):
        res = requests.get(f"{BASE_URL}/products/{active_product['product_id']}",
                           headers={"X-User-ID": USER_ID})
        assert res.status_code == 401

    def test_non_integer_roll_number_returns_400(self, active_product):
        res = requests.get(f"{BASE_URL}/products/{active_product['product_id']}",
                           headers={"X-Roll-Number": "xyz", "X-User-ID": USER_ID})
        assert res.status_code == 400

    def test_missing_user_id_returns_400(self, active_product):
        res = requests.get(f"{BASE_URL}/products/{active_product['product_id']}",
                           headers={"X-Roll-Number": ROLL})
        assert res.status_code == 400

    def test_non_existent_user_id_returns_400(self, active_product):
        res = requests.get(f"{BASE_URL}/products/{active_product['product_id']}",
                           headers={"X-Roll-Number": ROLL, "X-User-ID": "99999"})
        assert res.status_code == 400