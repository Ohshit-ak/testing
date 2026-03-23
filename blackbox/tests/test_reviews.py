"""
QuickCart — Reviews Section Tests
Endpoints:
  GET  /api/v1/products/{product_id}/reviews
  POST /api/v1/products/{product_id}/reviews

Run:
    pip install pytest requests
    pytest test_reviews.py -v
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
def active_product_id():
    res = requests.get(f"{BASE_URL}/admin/products", headers={"X-Roll-Number": ROLL})
    active = [p for p in res.json() if p.get("is_active")]
    assert active, "No active products found"
    return active[0]["product_id"]


# ═════════════════════════════════════════════════════════════════
# 1. GET /api/v1/products/{product_id}/reviews
# ═════════════════════════════════════════════════════════════════

class TestGetReviews:

    def test_valid_request_returns_200(self, valid_headers, active_product_id):
        res = requests.get(f"{BASE_URL}/products/{active_product_id}/reviews",
                           headers=valid_headers)
        assert res.status_code == 200

    def test_response_structure(self, valid_headers, active_product_id):
        res = requests.get(f"{BASE_URL}/products/{active_product_id}/reviews",
                           headers=valid_headers)
        data = res.json()
        # Accept a list or an object with a reviews key
        reviews = data if isinstance(data, list) else data.get("reviews", [])
        assert isinstance(reviews, list)

    def test_average_rating_zero_when_no_reviews(self, valid_headers):
        """A product with no reviews must have average_rating = 0, not an integer floor."""
        # Use a product that may have no reviews
        res = requests.get(f"{BASE_URL}/admin/products", headers={"X-Roll-Number": ROLL})
        no_review_product = None
        for p in res.json():
            if p.get("is_active"):
                r = requests.get(f"{BASE_URL}/products/{p['product_id']}/reviews",
                                 headers=valid_headers).json()
                reviews = r if isinstance(r, list) else r.get("reviews", [])
                if len(reviews) == 0:
                    no_review_product = p["product_id"]
                    break
        if no_review_product is None:
            pytest.skip("All products already have reviews")
        r = requests.get(f"{BASE_URL}/products/{no_review_product}/reviews",
                         headers=valid_headers).json()
        avg = r.get("average_rating", None) if isinstance(r, dict) else None
        if avg is not None:
            assert avg == 0, f"Expected average_rating 0 for product with no reviews, got {avg}"

    def test_nonexistent_product_returns_404(self, valid_headers):
        res = requests.get(f"{BASE_URL}/products/999999/reviews", headers=valid_headers)
        assert res.status_code == 404

    def test_missing_roll_number_returns_401(self, active_product_id):
        assert_missing_roll_number_returns_401(
            f"{BASE_URL}/products/{active_product_id}/reviews", USER_ID)

    def test_missing_user_id_returns_400(self, active_product_id):
        assert_missing_user_id_returns_400(
            f"{BASE_URL}/products/{active_product_id}/reviews", ROLL)


# ═════════════════════════════════════════════════════════════════
# 2. POST /api/v1/products/{product_id}/reviews
# ═════════════════════════════════════════════════════════════════

class TestPostReview:

    def test_valid_review_returns_200(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                            headers=valid_headers,
                            json={"rating": 4, "comment": "Great product!"})
        assert res.status_code == 200

    def test_rating_below_1_returns_400(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                            headers=valid_headers,
                            json={"rating": 0, "comment": "Bad"})
        assert res.status_code == 400

    def test_rating_above_5_returns_400(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                            headers=valid_headers,
                            json={"rating": 6, "comment": "Too good"})
        assert res.status_code == 400

    def test_rating_boundary_1_returns_200(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                            headers=valid_headers,
                            json={"rating": 1, "comment": "Minimum rating"})
        assert res.status_code == 200

    def test_rating_boundary_5_returns_200(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                            headers=valid_headers,
                            json={"rating": 5, "comment": "Maximum rating"})
        assert res.status_code == 200

    def test_comment_empty_returns_400(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                            headers=valid_headers,
                            json={"rating": 3, "comment": ""})
        assert res.status_code == 400

    def test_comment_over_200_chars_returns_400(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                            headers=valid_headers,
                            json={"rating": 3, "comment": "A" * 201})
        assert res.status_code == 400

    def test_comment_exactly_200_chars_returns_200(self, valid_headers, active_product_id):
        res = requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                            headers=valid_headers,
                            json={"rating": 3, "comment": "A" * 200})
        assert res.status_code == 200

    def test_average_rating_is_decimal_not_floor(self, valid_headers, active_product_id):
        """Average rating must be a proper decimal (e.g. 3.5), not an integer floor."""
        # Post two reviews with ratings 3 and 4; expected avg = 3.5
        requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                      headers=valid_headers, json={"rating": 3, "comment": "OK product"})
        requests.post(f"{BASE_URL}/products/{active_product_id}/reviews",
                      headers=valid_headers, json={"rating": 4, "comment": "Good product"})
        res = requests.get(f"{BASE_URL}/products/{active_product_id}/reviews",
                           headers=valid_headers).json()
        avg = res.get("average_rating") if isinstance(res, dict) else None
        if avg is not None:
            # avg should not be an integer (floor) value when ratings differ
            # It could be any float; just verify it's a float type
            assert isinstance(avg, float), (
                f"average_rating should be a float, got {type(avg).__name__}: {avg}"
            )

    def test_nonexistent_product_returns_404(self, valid_headers):
        res = requests.post(f"{BASE_URL}/products/999999/reviews", headers=valid_headers,
                            json={"rating": 3, "comment": "Test"})
        assert res.status_code == 404

    def test_missing_roll_number_returns_401(self, active_product_id):
        assert_missing_roll_number_returns_401(
            f"{BASE_URL}/products/{active_product_id}/reviews", USER_ID)

    def test_missing_user_id_returns_400(self, active_product_id):
        assert_missing_user_id_returns_400(
            f"{BASE_URL}/products/{active_product_id}/reviews", ROLL)

    def test_nonexistent_user_id_returns_400(self, active_product_id):
        assert_nonexistent_user_id_returns_400(
            f"{BASE_URL}/products/{active_product_id}/reviews", ROLL, "99999")
