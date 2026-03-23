"""
QuickCart — Reusable Header Validation Module

This module provides helper functions and fixtures for validating HTTP headers
according to the QuickCart API specification:

- X-Roll-Number: Must be a valid integer. Missing → 401, Invalid → 400.
- X-User-ID: Must be a positive integer matching an existing user. 
  Missing/Invalid/Non-existent → 400.

All non-admin endpoints require both headers.
Admin endpoints (/admin/*) only require X-Roll-Number.

Usage:
    from header_validation import (
        assert_missing_roll_number_returns_401,
        assert_invalid_roll_number_returns_400,
        assert_missing_user_id_returns_400,
        assert_invalid_user_id_returns_400,
        assert_nonexistent_user_id_returns_400,
    )

    endpoint = f"{BASE_URL}/profile"
    assert_missing_roll_number_returns_401(endpoint)
    assert_invalid_roll_number_returns_400(endpoint, USER_ID)
    ...
"""

import pytest
import requests


# ─────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def valid_headers(roll_number, user_id):
    """
    Returns valid headers for non-admin endpoints.
    
    Args:
        roll_number: Valid roll number as string
        user_id: Valid user ID as string
    
    Returns:
        dict: Headers with X-Roll-Number and X-User-ID
    """
    return {
        "X-Roll-Number": roll_number,
        "X-User-ID": user_id,
    }


@pytest.fixture(scope="session")
def admin_headers(roll_number):
    """
    Returns valid headers for admin endpoints.
    
    Args:
        roll_number: Valid roll number as string
    
    Returns:
        dict: Headers with only X-Roll-Number
    """
    return {
        "X-Roll-Number": roll_number,
    }


# ─────────────────────────────────────────────────────────────────
# X-ROLL-NUMBER VALIDATION HELPERS
# ─────────────────────────────────────────────────────────────────

def assert_missing_roll_number_returns_401(endpoint, user_id=None):
    """
    Test that missing X-Roll-Number header returns 401.
    
    Args:
        endpoint: Full endpoint URL
        user_id: Optional X-User-ID for non-admin endpoints
    
    Example:
        assert_missing_roll_number_returns_401(f"{BASE_URL}/profile", "1")
    """
    headers = {}
    if user_id:
        headers["X-User-ID"] = user_id
    
    res = requests.get(endpoint, headers=headers)
    assert res.status_code == 401, (
        f"Expected 401 for missing X-Roll-Number, got {res.status_code}"
    )


def assert_invalid_roll_number_returns_400(endpoint, user_id=None, roll_value="abc"):
    """
    Test that invalid X-Roll-Number header returns 400.
    
    Args:
        endpoint: Full endpoint URL
        user_id: Optional X-User-ID for non-admin endpoints
        roll_value: Invalid roll number value (default: "abc")
    
    Example:
        assert_invalid_roll_number_returns_400(f"{BASE_URL}/profile", "1", "abc")
    """
    headers = {"X-Roll-Number": roll_value}
    if user_id:
        headers["X-User-ID"] = user_id
    
    res = requests.get(endpoint, headers=headers)
    assert res.status_code == 400, (
        f"Expected 400 for invalid X-Roll-Number '{roll_value}', got {res.status_code}"
    )


def assert_invalid_roll_number_symbols_returns_400(endpoint, user_id=None):
    """
    Test that X-Roll-Number with symbols returns 400.
    
    Args:
        endpoint: Full endpoint URL
        user_id: Optional X-User-ID for non-admin endpoints
    
    Example:
        assert_invalid_roll_number_symbols_returns_400(f"{BASE_URL}/profile", "1")
    """
    assert_invalid_roll_number_returns_400(endpoint, user_id, "##!@")


# ─────────────────────────────────────────────────────────────────
# X-USER-ID VALIDATION HELPERS
# ─────────────────────────────────────────────────────────────────

def assert_missing_user_id_returns_400(endpoint, roll_number):
    """
    Test that missing X-User-ID header returns 400.
    
    Args:
        endpoint: Full endpoint URL
        roll_number: Valid X-Roll-Number value
    
    Example:
        assert_missing_user_id_returns_400(f"{BASE_URL}/profile", "12345")
    """
    headers = {"X-Roll-Number": roll_number}
    res = requests.get(endpoint, headers=headers)
    assert res.status_code == 400, (
        f"Expected 400 for missing X-User-ID, got {res.status_code}"
    )


def assert_invalid_user_id_returns_400(endpoint, roll_number, user_value="abc"):
    """
    Test that invalid X-User-ID (non-integer) returns 400.
    
    Args:
        endpoint: Full endpoint URL
        roll_number: Valid X-Roll-Number value
        user_value: Invalid user ID value (default: "abc")
    
    Example:
        assert_invalid_user_id_returns_400(f"{BASE_URL}/profile", "12345", "abc")
    """
    headers = {
        "X-Roll-Number": roll_number,
        "X-User-ID": user_value,
    }
    res = requests.get(endpoint, headers=headers)
    assert res.status_code == 400, (
        f"Expected 400 for invalid X-User-ID '{user_value}', got {res.status_code}"
    )


def assert_zero_user_id_returns_400(endpoint, roll_number):
    """
    Test that X-User-ID = 0 returns 400.
    
    Args:
        endpoint: Full endpoint URL
        roll_number: Valid X-Roll-Number value
    
    Example:
        assert_zero_user_id_returns_400(f"{BASE_URL}/profile", "12345")
    """
    assert_invalid_user_id_returns_400(endpoint, roll_number, "0")


def assert_negative_user_id_returns_400(endpoint, roll_number):
    """
    Test that negative X-User-ID returns 400.
    
    Args:
        endpoint: Full endpoint URL
        roll_number: Valid X-Roll-Number value
    
    Example:
        assert_negative_user_id_returns_400(f"{BASE_URL}/profile", "12345")
    """
    assert_invalid_user_id_returns_400(endpoint, roll_number, "-1")


def assert_nonexistent_user_id_returns_400(endpoint, roll_number, user_id="99999"):
    """
    Test that non-existent X-User-ID returns 400.
    
    Args:
        endpoint: Full endpoint URL
        roll_number: Valid X-Roll-Number value
        user_id: Non-existent user ID (default: "99999")
    
    Example:
        assert_nonexistent_user_id_returns_400(f"{BASE_URL}/profile", "12345", "99999")
    """
    headers = {
        "X-Roll-Number": roll_number,
        "X-User-ID": user_id,
    }
    res = requests.get(endpoint, headers=headers)
    assert res.status_code == 400, (
        f"Expected 400 for non-existent X-User-ID '{user_id}', got {res.status_code}"
    )


# ─────────────────────────────────────────────────────────────────
# COMBINED HEADER VALIDATION TEST
# ─────────────────────────────────────────────────────────────────

def assert_all_header_validations(endpoint, roll_number, user_id):
    """
    Run all header validation tests on a given endpoint.
    
    Tests:
      - Missing X-Roll-Number → 401
      - Invalid X-Roll-Number → 400
      - Invalid X-Roll-Number (symbols) → 400
      - Missing X-User-ID → 400
      - Invalid X-User-ID → 400
      - Zero/Negative/Non-existent X-User-ID → 400
    
    Args:
        endpoint: Full endpoint URL
        roll_number: Valid X-Roll-Number value
        user_id: Valid X-User-ID value (for comparison)
    
    Example:
        assert_all_header_validations(f"{BASE_URL}/profile", "12345", "1")
    """
    assert_missing_roll_number_returns_401(endpoint, user_id)
    assert_invalid_roll_number_returns_400(endpoint, user_id, "abc")
    assert_invalid_roll_number_symbols_returns_400(endpoint, user_id)
    assert_missing_user_id_returns_400(endpoint, roll_number)
    assert_invalid_user_id_returns_400(endpoint, roll_number, "abc")
    assert_zero_user_id_returns_400(endpoint, roll_number)
    assert_negative_user_id_returns_400(endpoint, roll_number)
    assert_nonexistent_user_id_returns_400(endpoint, roll_number, "99999")
